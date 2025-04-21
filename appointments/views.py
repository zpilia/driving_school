from django.views.generic import ListView, TemplateView
from .models import Appointment
from datetime import date

class AppointmentListView(ListView):
    model = Appointment
    template_name = 'appointments/list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        user = self.request.user
        return Appointment.objects.filter(student=user).order_by("date", "time")

class GeneralScheduleView(TemplateView):
    template_name = 'appointments/general_schedule.html'
