from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from my_driving_school.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('planning/', include(('planning.urls', 'planning'), namespace='planning')),
    path('lessonpackages/', include(('lessonpackages.urls', 'lessonpackages'), namespace='lessonpackages')),
    path('appointments/', include(('appointments.urls', 'appointments'), namespace='appointments')),
]
