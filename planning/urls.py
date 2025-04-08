from django.urls import path
from .views import ScheduleListView

urlpatterns = [
    path('', ScheduleListView.as_view(), name='schedule'),
]
