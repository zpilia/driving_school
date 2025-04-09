from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView 
from my_driving_school.views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LoginView.as_view(template_name='logout.html'), name='logout'),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('planning/', include('planning.urls')),
    path('lessonpackages/', include(('lessonpackages.urls', 'lessonpackages'), namespace='lessonpackages')),
    path('appointments/', include(('appointments.urls', 'appointments'), namespace='appointments')),
    path('accounts/password_reset/', include('django.contrib.auth.urls')),
]
