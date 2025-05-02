from django.urls import path
from .views import AppointmentListView, GeneralScheduleView, AppointmentRequestCreateView
from django.views.generic import TemplateView

urlpatterns = [
    path('', AppointmentListView.as_view(), name='list'),
    path('general/', GeneralScheduleView.as_view(), name='general_schedule'),
    path('request/', AppointmentRequestCreateView.as_view(), name='request_appointment'),
]
