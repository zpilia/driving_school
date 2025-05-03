from django.views.generic import ListView
from django.db.models import Case, When, Value, IntegerField
from appointments.models import Appointment

from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import CustomUser
from datetime import datetime, timedelta
import calendar

class ScheduleListView(ListView):
    model = Appointment
    template_name = 'planning/schedule_list.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        if user.role == 'student':
            qs = Appointment.objects.filter(student=user)
        elif user.role == 'instructor':
            qs = Appointment.objects.filter(instructor=user)
        elif user.role in ['secretary', 'admin']:
            qs = Appointment.objects.all()
        else:
            qs = Appointment.objects.none()

        return qs.annotate(
            status_order=Case(
                When(status='scheduled', then=Value(1)),
                When(status='completed', then=Value(2)),
                When(status='cancelled', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        ).order_by('status_order', '-date', '-time')


@login_required
def global_planning_view(request, year=None, month=None):
    if not year or not month:
        now = timezone.now()
        year = now.year
        month = now.month

    month_days = calendar.monthcalendar(year, month)
    instructors = CustomUser.objects.filter(role='instructor')

    appointments = Appointment.objects.filter(date__year=year, date__month=month)

    time_slots = []
    for instructor in instructors:
        start_time = datetime.strptime('09:00:00', '%H:%M:%S').time()
        end_time = datetime.strptime('17:00:00', '%H:%M:%S').time()
        lunch_start = datetime.strptime('12:00:00', '%H:%M:%S').time()
        lunch_end = datetime.strptime('13:00:00', '%H:%M:%S').time()

        current_time = datetime.combine(datetime.today(), start_time)
        while current_time.time() < end_time:
            if current_time.time() < lunch_start or current_time.time() >= lunch_end:
                time_slots.append((instructor, current_time))
            current_time += timedelta(minutes=30)

    appointments_by_day = {}
    for app in appointments:
        day = app.date.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(app)

    context = {
        'month_days': month_days,
        'appointments_by_day': appointments_by_day,
        'time_slots': time_slots,
        'current_month': month,
        'current_year': year,
        'months': calendar.month_name,
    }

    return render(request, 'planning/global_planning_view.html', context)
