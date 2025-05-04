from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, Http404
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import AppointmentRequest
from .forms import AppointmentRequestForm, AppointmentRequestUpdateForm, AppointmentForm

from accounts.decorators import role_required
from django.views.generic import DeleteView
from lessonpackages.models import LessonPackage

from django.shortcuts import render
from django.utils import timezone
from .models import Appointment
from django.contrib.auth import get_user_model
User = get_user_model()
from datetime import datetime, timedelta


class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Appointment.objects.filter(student=user)
        elif user.role == 'instructor':
            return Appointment.objects.filter(instructor=user)
        elif user.role in ['secretary', 'admin']:
            return Appointment.objects.all()
        else:
            return Appointment.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # On ajoute les demandes de rendez-vous selon le rôle
        if user.role == 'instructor':
            context['requests'] = AppointmentRequest.objects.filter(instructor=user)
        elif user.role == 'student':
            context['requests'] = AppointmentRequest.objects.filter(student=user)
        elif user.role in ['secretary', 'admin']:
            context['requests'] = AppointmentRequest.objects.all()

        return context

@method_decorator(login_required, name='dispatch')
class AppointmentRequestCreateView(CreateView):
    model = AppointmentRequest
    form_class = AppointmentRequestForm
    template_name = 'appointments/appointment_request_form.html'
    success_url = reverse_lazy('appointments:request_appointment')

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.instance.status = 'pending'
        messages.success(self.request, "Votre demande de rendez-vous a bien été envoyée.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Une erreur est survenue. Veuillez vérifier le formulaire.")
        return super().form_invalid(form)

class AppointmentRequestUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AppointmentRequest
    form_class = AppointmentRequestUpdateForm
    template_name = 'appointments/appointment_request_update.html'
    success_url = reverse_lazy('appointments:list')

    def test_func(self):
        appointment = self.get_object()
        user = self.request.user
        return user == appointment.student or user == appointment.instructor

    def dispatch(self, request, *args, **kwargs):
        appointment = self.get_object()
        if appointment.status in ['accepted', 'refused']:
            messages.warning(request, "Cette demande est déjà finalisée.")
            return redirect('appointments:list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "La demande a été mise à jour avec succès.")
        return super().form_valid(form)

class AppointmentRequestListView(LoginRequiredMixin, ListView):
    model = AppointmentRequest
    template_name = 'appointments/appointment_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return AppointmentRequest.objects.filter(instructor=self.request.user)


@method_decorator(role_required(['secretary', 'admin', 'instructor']), name='dispatch')
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def get_success_url(self):
        if self.request.user.role == 'instructor':
            return reverse_lazy('planning:instructor_schedule', kwargs={'instructor_id': self.request.user.id})
        return reverse_lazy('appointments:manage')

    def get_initial(self):
        initial = super().get_initial()

        instructor_id = self.request.GET.get('instructor')
        date = self.request.GET.get('date')
        time = self.request.GET.get('time')

        if instructor_id:
            instructor = get_object_or_404(User, id=instructor_id)
            initial['instructor'] = instructor

        if date:
            initial['date'] = date

        if time:
            initial['time'] = time

        return initial

    def dispatch(self, request, *args, **kwargs):
        if request.user.role in ['secretary', 'admin']:
            return super().dispatch(request, *args, **kwargs)

        instructor_id = self.request.GET.get('instructor')
        if instructor_id:
            instructor = get_object_or_404(User, id=instructor_id)
            if instructor != request.user:
                raise Http404("Vous n'êtes pas autorisé à créer ce rendez-vous.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        student = form.cleaned_data['student']
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']

        conflicting_appointments = Appointment.objects.filter(student=student, date=date, time=time)
        if conflicting_appointments.exists():
            messages.error(self.request, "Cet étudiant a déjà un rendez-vous à cette date et heure.")
            return self.form_invalid(form)

        lesson_package = LessonPackage.objects.filter(student=student).first()

        if lesson_package and lesson_package.paid_hours > lesson_package.used_hours:
            messages.success(self.request, "Rendez-vous créé avec succès.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Cet étudiant n'a pas d'heures payées disponibles.")
            return self.form_invalid(form)


@method_decorator(role_required(['secretary', 'admin', 'instructor']), name='dispatch')
class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def get_success_url(self):
        if self.request.user.role == 'instructor':
            return reverse_lazy('planning:instructor_schedule', kwargs={'instructor_id': self.request.user.id})
        return reverse_lazy('appointments:manage')

    def dispatch(self, request, *args, **kwargs):
        appointment = self.get_object()

        if request.user.role == 'instructor':
            if appointment.instructor != request.user:
                raise Http404("Vous n'êtes pas autorisé à modifier ce rendez-vous.")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        student = form.cleaned_data['student']
        date = form.cleaned_data['date']
        time = form.cleaned_data['time']

        conflicting_appointments = Appointment.objects.filter(student=student, date=date, time=time).exclude(
            id=self.object.id)
        if conflicting_appointments.exists():
            messages.error(self.request, "Cet étudiant a déjà un rendez-vous à cette date et heure.")
            return self.form_invalid(form)

        lesson_package = LessonPackage.objects.filter(student=student).first()

        if lesson_package and lesson_package.paid_hours > lesson_package.used_hours:
            messages.success(self.request, "Rendez-vous modifié avec succès.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Cet étudiant n'a pas d'heures payées disponibles.")
            return self.form_invalid(form)


@method_decorator(role_required(['secretary', 'admin', 'instructor']), name='dispatch')
class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'

    def get_success_url(self):
        if self.request.user.role == 'instructor':
            return reverse_lazy('planning:instructor_schedule', kwargs={'instructor_id': self.request.user.id})
        return reverse_lazy('appointments:manage')

    def dispatch(self, request, *args, **kwargs):
        appointment = self.get_object()
        if request.user.role == 'instructor':
            if appointment.instructor != request.user:
                raise Http404("Vous n'êtes pas autorisé à supprimer ce rendez-vous.")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Rendez-vous supprimé avec succès.")
        return super().delete(request, *args, **kwargs)

@method_decorator(role_required(['secretary', 'admin']), name='dispatch')
class AppointmentView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/manage.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        return Appointment.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
@role_required(['secretary', 'admin'])
def add_appointment(request):
    date_str = request.GET.get('date')
    time = request.GET.get('time')

    if not date_str or not time:
        return redirect('planning:general_schedule_default')

    date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()

    instructors = User.objects.filter(role='instructor')

    instructor_availability = []

    for instructor in instructors:
        appointment = Appointment.objects.filter(instructor=instructor, date=date, time=time).first()

        if appointment:
            instructor_availability.append({
                'instructor': instructor,
                'available': False,
                'student': appointment.student,
                'location': appointment.location
            })
        else:
            instructor_availability.append({
                'instructor': instructor,
                'available': True,
                'student': None,
                'location': None
            })

    context = {
        'date': date,
        'time': time,
        'instructor_availability': instructor_availability,
        'form': AppointmentForm(initial={'date': date, 'time': time}),
    }

    return render(request, 'appointments/add_appointment.html', context)


