from django.urls import path
from .views import AppointmentListView, GeneralScheduleView

urlpatterns = [
    path('', AppointmentListView.as_view(), name='list'),
    path('general/', GeneralScheduleView.as_view(), name='general_schedule'),
]
