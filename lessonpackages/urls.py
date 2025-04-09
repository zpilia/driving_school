from django.urls import path
from .views import LessonPackageManageView  # Cette vue doit être implémentée (même en stub)

urlpatterns = [
    path('manage/', LessonPackageManageView.as_view(), name='manage'),
    path('', LessonPackageManageView.as_view(), name='list'),  # Vue par défaut pour lister les leçons
    path('create/', LessonPackageManageView.as_view(), name='create'),  # Vue pour créer un package de leçons
]
