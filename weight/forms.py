from django import forms
from .models import WeightEntry

class WeightEntryForm(forms.ModelForm):
    class Meta:
        model = WeightEntry
        fields = ['weight_kg', 'date']
        widgets = {
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 70.5',
                'step': '0.01'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'weight_kg': 'Peso (kg)',
            'date': 'Data',
        }