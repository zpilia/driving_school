from pyexpat.errors import messages
from django.contrib import messages
from django.views.generic import TemplateView, CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import AppointmentRequest
from .forms import AppointmentRequestForm

class AppointmentListView(TemplateView):
    template_name = 'appointments/list.html'

class GeneralScheduleView(TemplateView):
    template_name = 'appointments/general_schedule.html'

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