from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .decorators import role_required
from .forms import CustomUserCreationForm, CustomUserForm
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

# -------------------------------
# DASHBOARD VIEWS PAR ROLE
# -------------------------------

@login_required
@role_required(['student'])
def student_dashboard(request):
    appointments = Appointment.objects.filter(student=request.user)
    # Retrieve the next scheduled appointment for the logged-in student
    next_appointment = (
        Appointment.objects
        .filter(student=request.user, status='scheduled')
        .order_by('date', 'time')
        .first()
    )

    # Retrieve all lesson packages linked to the student
    lesson_packages = LessonPackage.objects.filter(student=request.user)

    # ➔ Chercher le premier forfait en cours (progression < 100%)
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
        'next_appointment': next_appointment,
        'lesson_packages': lesson_packages,
        'forfait_en_cours': forfait_en_cours,  # Ajout de l'avancement
    }
    return render(request, 'dashboard_student.html', context)


@login_required
@role_required(['instructor'])
def instructor_dashboard(request):
    # Récupère les rendez-vous pour l'instructeur connecté
    appointments = Appointment.objects.filter(instructor=request.user)
    context = {
        'user': request.user,
        'appointments': appointments,
    }
    return render(request, 'dashboard_instructor.html', context)

@login_required
@role_required(['secretary'])
def secretary_dashboard(request):
    # Récupère la liste des étudiants
    students = CustomUser.objects.filter(role='student')
    context = {
        'user': request.user,
        'students': students,
    }
    return render(request, 'dashboard_secretary.html', context)

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    # Récupère la liste des étudiants, instructeurs et secrétaires
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
    # Redirige vers le dashboard correspondant au rôle de l'utilisateur
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
        queryset = CustomUser.objects.filter(role__in=['student', 'instructor'])

        search = self.request.GET.get('search', '')
        roles = self.request.GET.getlist('role')  # Liste des rôles sélectionnés
        is_active = self.request.GET.get('is_active')  # Valeur pour le filtre 'actif'

        # Filtrage par recherche (nom, prénom, email, etc.)
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
            reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
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



def create_account_and_send_email(request):
    """
    Vue permettant à un admin de créer un compte sans mot de passe,
    d'envoyer un email à l'utilisateur pour qu'il puisse définir son mot de passe.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Définir un mot de passe inutilisable pour empêcher l'accès avant validation
            user.set_unusable_password()
            user.save()
            # Générer le token et uidb64 pour le processus de réinitialisation
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            # Construire l'URL de réinitialisation (password_reset_confirm est fourni par Django)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            )
            subject = "Activate your account - Set your password"
            message = f"Hello {user.username},\n\n" \
                      f"Please click on the link below to set your password and activate your account:\n" \
                      f"{reset_url}\n\n" \
                      f"Thank you."
            # Envoyer l'email (Assurez-vous que vos paramètres EMAIL_* sont configurés dans settings.py)
            send_mail(subject, message, 'no-reply@yourdomain.com', [user.email])
            return redirect('accounts:account_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/create_account_email.html', {'form': form})