from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import AppointmentRequest
from .forms import AppointmentRequestForm, AppointmentRequestUpdateForm, AppointmentForm

from .models import Appointment
from accounts.decorators import role_required
from django.views.generic import DeleteView
from lessonpackages.models import LessonPackage


class GeneralScheduleView(TemplateView):
    template_name = 'appointments/general_schedule.html'

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



@method_decorator(role_required(['secretary', 'admin']), name='dispatch')
class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointments:manage')

    def form_valid(self, form):
        student = form.cleaned_data['student']

        lesson_package = LessonPackage.objects.filter(student=student).first()

        if lesson_package and lesson_package.paid_hours > lesson_package.used_hours:
            messages.success(self.request, "Rendez-vous créé avec succès.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Cet étudiant n'a pas d'heures payées disponibles.")
            return self.form_invalid(form)


@method_decorator(role_required(['secretary', 'admin']), name='dispatch')
class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'
    success_url = reverse_lazy('appointments:manage')

    def form_valid(self, form):
        student = form.cleaned_data['student']

        lesson_package = LessonPackage.objects.filter(student=student).first()

        if lesson_package and lesson_package.paid_hours > lesson_package.used_hours:
            messages.success(self.request, "Rendez-vous modifié avec succès.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Cet étudiant n'a pas d'heures payées disponibles.")
            return self.form_invalid(form)

@method_decorator(role_required(['secretary', 'admin']), name='dispatch')
class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = 'appointments/appointment_confirm_delete.html'
    success_url = reverse_lazy('appointments:manage')

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
