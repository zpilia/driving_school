from django.urls import path
from .views import AppointmentListView, GeneralScheduleView, AppointmentRequestCreateView, AppointmentRequestUpdateView, \
    AppointmentRequestListView
from django.views.generic import TemplateView

urlpatterns = [
    path('', AppointmentListView.as_view(), name='list'),
    path('general/', GeneralScheduleView.as_view(), name='general_schedule'),
    path('request/', AppointmentRequestCreateView.as_view(), name='request_appointment'),
    path('request/<int:pk>/update/', AppointmentRequestUpdateView.as_view(), name='request_update'),
]
