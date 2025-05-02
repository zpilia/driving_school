from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import AppointmentRequest
from .forms import AppointmentRequestForm, AppointmentRequestUpdateForm

from .models import Appointment

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
        messages.success(self.request, "Your appointment request has been sent successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "There was an error with your submission. Please check the form.")
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
        messages.success(self.request, "Proposition mise à jour avec succès.")
        return super().form_valid(form)

class AppointmentRequestListView(LoginRequiredMixin, ListView):
    model = AppointmentRequest
    template_name = 'appointments/appointment_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return AppointmentRequest.objects.filter(instructor=self.request.user)