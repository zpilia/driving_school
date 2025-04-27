from django.views.generic import TemplateView

class AppointmentListView(TemplateView):
    template_name = 'appointments/list.html'

class GeneralScheduleView(TemplateView):
    template_name = 'appointments/general_schedule.html'