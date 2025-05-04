from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role')

class CustomUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    }))
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, widget=forms.Select(attrs={
        'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    }))
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_classes = 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = field_classes
            self.fields['username'].label = "Nom d'utilisateur"
            self.fields['email'].label = "Adresse email"
            self.fields['role'].label = "Rôle"
            self.fields['first_name'].label = "Prénom"
            self.fields['last_name'].label = "Nom"
