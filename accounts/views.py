from datetime import timedelta
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import Http404

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode


from .decorators import role_required
from .forms import CustomUserCreationForm, CustomUserForm, CustomSetPasswordForm
from .models import CustomUser

# Import des modèles provenant d'autres applications
from appointments.models import Appointment
from lessonpackages.models import LessonPackage

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404

# -------------------------------
# DASHBOARD VIEWS PAR ROLE
# -------------------------------

@login_required
@role_required(['student'])
def student_dashboard(request):
    appointments = (
        Appointment.objects
        .filter(student=request.user, status='scheduled', date__gte=timezone.now().date())
        .order_by('date', 'time')[:5]
    )

    next_appointment = appointments.first()

    lesson_packages = LessonPackage.objects.filter(student=request.user)

    forfait_en_cours = None
    for package in lesson_packages:
        if package.total_hours > 0:
            progression = (package.used_hours / package.total_hours) * 100
            if progression < 100:
                forfait_en_cours = {
                    'package': package,
                    'heures_achetees': package.total_hours,
                    'heures_utilisees': package.used_hours,
                    'progression': progression,
                }
                break

    context = {
        'user': request.user,
        'appointments': appointments,
        'next_appointment': next_appointment,
        'lesson_packages': lesson_packages,
        'forfait_en_cours': forfait_en_cours,
    }
    return render(request, 'dashboard_student.html', context)


@login_required
@role_required(['instructor'])
def instructor_dashboard(request):
    appointments = (
        Appointment.objects
        .filter(instructor=request.user, status='scheduled', date__gte=timezone.now().date())
        .order_by('date', 'time')[:5]
    )

    next_appointment = appointments.first()

    context = {
        'user': request.user,
        'appointments': appointments,
        'next_appointment': next_appointment,
    }
    return render(request, 'dashboard_instructor.html', context)

@login_required
@role_required(['secretary'])
def secretary_dashboard(request):
    students = CustomUser.objects.filter(role='student')

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_date_formatted = start_of_week.strftime('%Y-%m-%d')

    context = {
        'user': request.user,
        'students': students,
        'start_date': start_of_week,
        'today': today,
    }
    return render(request, 'dashboard_secretary.html', context)

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    students = CustomUser.objects.filter(role='student')
    instructors = CustomUser.objects.filter(role='instructor')
    secretaries = CustomUser.objects.filter(role='secretary')
    context = {
        'user': request.user,
        'students': students,
        'instructors': instructors,
        'secretaries': secretaries,
    }
    return render(request, 'dashboard_admin.html', context)

@login_required
def dashboard_view(request):
    if request.user.role == 'student':
        return student_dashboard(request)
    elif request.user.role == 'instructor':
        return instructor_dashboard(request)
    elif request.user.role == 'secretary':
        return secretary_dashboard(request)
    elif request.user.role == 'admin':
        return admin_dashboard(request)
    else:
        return render(request, 'dashboard_default.html', {'user': request.user})

# -------------------------------
# INSCRIPTION & PROFIL
# -------------------------------

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    role = user.role.lower()
    template_name = f'profiles/{role}.html'
    return render(request, template_name, {'user': user})

# -------------------------------
# VUES CRUD POUR LA GESTION DES COMPTES
# (Accessible aux secrétaires et admin)
# -------------------------------

def secretary_or_admin_required(function):
    return role_required(['secretary', 'admin'])(function)

@method_decorator(secretary_or_admin_required, name='dispatch')
class AccountListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'
    def get_queryset(self):
        search = self.request.GET.get('search', '')
        roles = self.request.GET.getlist('role')
        is_active = self.request.GET.get('is_active')

        if self.request.user.role == 'admin':
            queryset = CustomUser.objects.all()
        elif self.request.user.role == 'secretary':
            queryset = CustomUser.objects.filter(role__in=['student', 'instructor'])
        else:
            queryset = CustomUser.objects.none()

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )

        if roles:
            queryset = queryset.filter(role__in=roles)

        if is_active == '1':
            queryset = queryset.filter(is_active=True)
        elif is_active == '0':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_roles'] = self.request.GET.getlist('role')
        context['search'] = self.request.GET.get('search', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        return context

@method_decorator(secretary_or_admin_required, name='dispatch')
class AccountCreateView(LoginRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_unusable_password()
        user.save()

        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = self.request.build_absolute_uri(
            reverse('accounts:reset_password', kwargs={'uidb64': uidb64, 'token': token})
        )

        subject = "Activation de votre compte - Auto-école"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        text_content = f"""
        Bonjour {user.first_name},

        Un compte a été créé pour vous sur notre plateforme.

        Veuillez cliquer sur le lien suivant pour définir votre mot de passe :
        {reset_url}

        Merci,
        L'équipe de l'auto-école
        """

        html_content = f"""
        <p>Bonjour {user.first_name},</p>
        <p>Un compte a été créé pour vous sur notre plateforme.</p>
        <p><a href="{reset_url}">Cliquez ici pour définir votre mot de passe</a></p>
        <p>Merci,<br>L'équipe de l'auto-école</p>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print(f"Email envoyé à {user.email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")

        return super().form_valid(form)


@method_decorator(secretary_or_admin_required, name='dispatch')
class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

@method_decorator(secretary_or_admin_required, name='dispatch')
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:account_list')

    def form_valid(self, form):
        user = self.get_object()

        subject = "Suppression de votre compte - Auto-école"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        text_content = f"""
        Bonjour {user.first_name},

        Votre compte a été supprimé sur notre plateforme.

        Si vous avez des questions, n'hésitez pas à nous contacter.

        Merci,
        L'équipe de l'auto-école
        """

        html_content = f"""
        <p>Bonjour {user.first_name},</p>
        <p>Votre compte a été supprimé sur notre plateforme.</p>
        <p>Si vous avez des questions, n'hésitez pas à nous contacter.</p>
        <p>Merci,<br>L'équipe de l'auto-école</p>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
            print(f"Email envoyé à {user.email}")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")

        user.delete()

        return super().form_valid(form)


@login_required
@role_required(['secretary', 'admin', 'instructor'])
def student_infos(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    appointments = Appointment.objects.filter(student=student)
    lesson_package = LessonPackage.objects.filter(student=student).first()

    context = {
        'student': student,
        'appointments': appointments,
        'lesson_package': lesson_package,
    }

    return render(request, 'profiles/student_infos.html', context)


# -------------------------------
# VUES STUB POUR LA GESTION DES COMPTES
# -------------------------------

@login_required
@role_required(['secretary', 'admin'])
def manage_accounts_view(request):
    return render(request, 'accounts/manage_accounts.html', {'user': request.user})

@login_required
@role_required(['admin'])
def manage_secretaries_view(request):
    return render(request, 'accounts/manage_secretaries.html', {'user': request.user})



def reset_password(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        raise Http404("Utilisateur non trouvé")

    if not default_token_generator.check_token(user, token):
        messages.error(request, "Le lien de réinitialisation du mot de passe est invalide ou expiré.")
        return redirect('home')

    if request.method == 'POST':

        form = CustomSetPasswordForm(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès.")
            return redirect('home')
    else:
        form = CustomSetPasswordForm(user=user)

    context = {
        'form': form,
        'uidb64': uidb64,
        'token': token,
    }
    return render(request, 'accounts/password_reset_form.html', context)