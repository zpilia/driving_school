from django.urls import path
from .views import ScheduleListView, general_schedule, instructor_schedule

urlpatterns = [
    path('schedule/', ScheduleListView.as_view(), name='schedule'),
    path('general/', general_schedule, name='general_schedule_default'),
    path('general/<str:start_date>/', general_schedule, name='general_schedule'),
    path('instructor/<int:instructor_id>/', instructor_schedule, name='instructor_schedule'),
]
