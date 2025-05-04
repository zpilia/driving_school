from django.urls import path
from .views import LessonPackageManageView, LessonPackageProgressView, AddHoursView

urlpatterns = [
    path('manage/', LessonPackageManageView.as_view(), name='manage'),
    path('', LessonPackageManageView.as_view(), name='list'),
    path('create/', LessonPackageManageView.as_view(), name='create'),
    path('progress/', LessonPackageProgressView.as_view(), name='lessonpackage_progress'),
    path('add_hours/<int:pk>/', AddHoursView.as_view(), name='add_hours'),

]