from django.urls import path
from .views import LessonPackageManageView, LessonPackageProgressView

urlpatterns = [
    path('manage/', LessonPackageManageView.as_view(), name='manage'),
    path('', LessonPackageManageView.as_view(), name='list'),  # Vue par défaut pour lister les leçons
    path('create/', LessonPackageManageView.as_view(), name='create'),  # Vue pour créer un package de leçons
    path('progress/', LessonPackageProgressView.as_view(), name='lessonpackage_progress'),  # Vue pour l'avancement
]