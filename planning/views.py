from django.views.generic import ListView
from django.db.models import Case, When, Value, IntegerField
from appointments.models import Appointment

class ScheduleListView(ListView):
    model = Appointment
    template_name = 'planning/schedule_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        # Filter appointments based on the user's role
        if user.role == 'student':
            qs = Appointment.objects.filter(student=user)
        elif user.role == 'instructor':
            qs = Appointment.objects.filter(instructor=user)
        elif user.role in ['secretary', 'admin']:
            qs = Appointment.objects.all()
        else:
            qs = Appointment.objects.none()

        # Add a custom order field for statuses
        return qs.annotate(
            status_order=Case(
                When(status='scheduled', then=Value(1)),
                When(status='completed', then=Value(2)),
                When(status='cancelled', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('status_order', '-date', '-time')