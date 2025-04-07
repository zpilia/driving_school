from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .decorators import role_required
from .forms import CustomUserCreationForm
from django.contrib.auth import login

@login_required
@role_required(['student'])
def student_dashboard(request):
    return render(request, 'dashboard_student.html', {'user': request.user})

@login_required
@role_required(['instructor'])
def instructor_dashboard(request):
    return render(request, 'dashboard_instructor.html', {'user': request.user})

@login_required
@role_required(['secretary'])
def secretary_dashboard(request):
    return render(request, 'dashboard_secretary.html', {'user': request.user})

@login_required
@role_required(['admin'])
def admin_dashboard(request):
    return render(request, 'dashboard_admin.html', {'user': request.user})

@login_required
def dashboard_view(request):
    if request.user.role == 'student':
        return student_dashboard(request)
    elif request.user.role == 'instructor':
        return instructor_dashboard(request)
    elif request.user.role == 'secretary':
        return secretary_dashboard(request)
    elif request.user.role == 'admin':
        return admin_dashboard(request)
    else:
        return render(request, 'dashboard_default.html', {'user': request.user})

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})
