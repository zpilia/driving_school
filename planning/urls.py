from django.urls import path
from .views import ScheduleListView

urlpatterns = [
    path('my_schedule/', ScheduleListView.as_view(), name='schedule'),
]
