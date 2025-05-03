from django.urls import path
from .views import (AppointmentListView,
                    GeneralScheduleView,
                    AppointmentRequestCreateView,
                    AppointmentRequestUpdateView, \
                    AppointmentRequestListView,
                    AppointmentCreateView,
                    AppointmentUpdateView,
                    AppointmentDeleteView,
                    AppointmentView,
                    weekly_schedule

                    )
from django.views.generic import TemplateView

urlpatterns = [
    path('', AppointmentListView.as_view(), name='list'),
    path('general/', GeneralScheduleView.as_view(), name='general_schedule'),
    path('request/', AppointmentRequestCreateView.as_view(), name='request_appointment'),
    path('request/<int:pk>/update/', AppointmentRequestUpdateView.as_view(), name='request_update'),
    path('create/', AppointmentCreateView.as_view(), name='create_appointment'),
    path('<int:pk>/edit/', AppointmentUpdateView.as_view(), name='edit_appointment'),
    path('<int:pk>/delete/', AppointmentDeleteView.as_view(), name='delete_appointment'),
    path('manage/', AppointmentView.as_view(), name='manage'),
    path('weekly/<str:start_date>/', weekly_schedule, name='weekly_schedule'),

]
