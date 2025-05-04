from django import forms
from .models import AppointmentRequest, Appointment
from accounts.models import CustomUser
from django.forms.widgets import DateInput, TimeInput
from django.db.models import F
from lessonpackages.models import LessonPackage

class AppointmentRequestForm(forms.ModelForm):
    instructor = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='instructor'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = AppointmentRequest
        fields = ['instructor', 'date', 'time', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
        }

class AppointmentRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ['date', 'time', 'location', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class AppointmentForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='student').filter(
            lesson_packages__paid_hours__gt=F('lesson_packages__used_hours')
        ).distinct(),
        widget=forms.Select(attrs={
            'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
        }),
        label="Étudiant"
    )
    instructor = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='instructor'),
        widget=forms.Select(attrs={
            'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
        }),
        label="Instructeur"
    )

    class Meta:
        model = Appointment
        fields = ['student', 'instructor', 'date', 'time', 'location', 'status']
        widgets = {
            'date': DateInput(attrs={
                'type': 'date',
                'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
            }, format='%Y-%m-%d'),
            'time': TimeInput(attrs={
                'type': 'time',
                'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
            }, format='%H:%M'),
            'location': forms.TextInput(attrs={
                'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-600'
            }),
        }
        labels = {
            'date': 'Date',
            'time': 'Heure',
            'location': 'Lieu',
            'status': 'Statut',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['date'].initial = self.instance.date
            self.fields['time'].initial = self.instance.time