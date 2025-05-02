from django import forms
from .models import AppointmentRequest
from accounts.models import CustomUser

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
