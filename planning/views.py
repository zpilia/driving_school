from django.views.generic import ListView
from appointments.models import Appointment

class ScheduleListView(ListView):
    model = Appointment
    template_name = 'planning/schedule_list.html'
    context_object_name = 'appointments'

    def get_queryset(self):
        user = self.request.user
        # Filter appointments based on the user's role
        if user.role == 'student':
            return Appointment.objects.filter(student=user)
        elif user.role == 'instructor':
            return Appointment.objects.filter(instructor=user)
        elif user.role in ['secretary', 'admin']:
            return Appointment.objects.all()
        else:
            return Appointment.objects.none()
