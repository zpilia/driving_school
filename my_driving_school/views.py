# my_driving_school/views.py
from django.shortcuts import redirect

def home(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    else:
        return redirect('login')
