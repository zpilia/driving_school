from django.views.generic import ListView
from django.db.models import Case, When, Value, IntegerField
from appointments.models import Appointment

from django.shortcuts import render, get_object_or_404,  redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta
from accounts.decorators import role_required
from django.contrib.auth import get_user_model
User = get_user_model()



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
@role_required(['secretary', 'admin'])
def general_schedule(request, start_date=None):
    today = timezone.now().date()

    if not start_date:
        start_of_week = today - timedelta(days=today.weekday())
    else:
        start_of_week = datetime.strptime(start_date, '%Y-%m-%d').date()

    end_of_week = start_of_week + timedelta(days=5)
    week_days = [start_of_week + timedelta(days=i) for i in range(6)]
    schedule_slots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']

    appointments = Appointment.objects.filter(date__range=[start_of_week, end_of_week])
    total_instructors = User.objects.filter(role='instructor').count()

    schedule = {}
    appointments_dict = {}

    for day in week_days:
        day_str = str(day)
        schedule[day_str] = {}
        for time in schedule_slots:
            if time == '12:00':
                schedule[day_str][time] = 'pause'
            else:
                booked_appointments = appointments.filter(date=day, time=time)
                appointments_dict[f"{day}_{time}"] = booked_appointments.first()

                if booked_appointments.count() >= total_instructors:
                    schedule[day_str][time] = 'full'
                else:
                    schedule[day_str][time] = 'available'

    instructors = User.objects.filter(role='instructor')

    prev_week_date = (start_of_week - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week_date = (start_of_week + timedelta(days=7)).strftime('%Y-%m-%d')

    context = {
        'schedule': schedule,
        'schedule_slots': schedule_slots,
        'week_days': week_days,
        'appointments_dict': appointments_dict,
        'instructors': instructors,
        'week_range': f"Semaine du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m')}",
        'prev_week_date': prev_week_date,
        'next_week_date': next_week_date,
    }

    return render(request, 'planning/general_schedule.html', context)

@login_required
@role_required(['secretary', 'admin', 'instructor'])
def instructor_schedule(request, instructor_id=None):
    user = request.user

    if instructor_id is None:
        if user.role == 'instructor':
            instructor = user
        else:
            return redirect('home')
    else:
        instructor = get_object_or_404(User, id=instructor_id, role='instructor')
        if user.role == 'instructor' and instructor != user:
            return redirect('home')

    today = timezone.now().date()
    start_date_str = request.GET.get('start_date')
    if not start_date_str:
        start_of_week = today - timedelta(days=today.weekday())
    else:
        start_of_week = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    end_of_week = start_of_week + timedelta(days=5)
    week_days = [start_of_week + timedelta(days=i) for i in range(6)]
    schedule_slots = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00']

    appointments = Appointment.objects.filter(
        instructor=instructor,
        date__range=[start_of_week, end_of_week]
    )

    schedule = {}
    for day in week_days:
        day_str = str(day)
        schedule[day_str] = {}
        for time in schedule_slots:
            if time == '12:00':
                schedule[day_str][time] = 'pause'
            else:
                appointment = appointments.filter(date=day, time=time).first()
                if appointment:
                    student_name = appointment.student.get_full_name()
                    location = appointment.location if hasattr(appointment, 'location') else 'Lieu inconnu'
                    student_id = appointment.student.id
                    schedule[day_str][time] = f"<a href='/accounts/students/{student_id}/infos/'>{student_name}</a><br><span class='text-xs text-gray-600'>{location}</span>"
                else:
                    schedule[day_str][time] = 'available'

    prev_week_date = (start_of_week - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week_date = (start_of_week + timedelta(days=7)).strftime('%Y-%m-%d')

    context = {
        'instructor': instructor,
        'schedule': schedule,
        'schedule_slots': schedule_slots,
        'week_days': week_days,
        'week_range': f"Semaine du {start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m')}",
        'prev_week_date': prev_week_date,
        'next_week_date': next_week_date,
    }

    return render(request, 'planning/instructor_schedule.html', context)


