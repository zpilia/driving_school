from django import forms

class AddHoursForm(forms.Form):
    hours = forms.FloatField(
        min_value=0,
        label="Nombre d'heures",
        required=True,
        widget=forms.NumberInput(attrs={'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'})
    )

    payment_status = forms.ChoiceField(
        choices=[('unpaid', 'Non payé'), ('paid', 'Payé')],
        required=True,
        label="Statut du paiement",
        initial='unpaid',
        widget=forms.Select(attrs={'class': 'w-full p-3 mt-1 mb-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 mb-4'})
    )

    def clean(self):
        cleaned_data = super().clean()
        hours = cleaned_data.get('hours')

        if hours <= 0:
            raise forms.ValidationError('Veuillez entrer un nombre d\'heures valide.')

        return cleaned_data

