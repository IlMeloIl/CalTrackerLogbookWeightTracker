from django import forms
from .models import Food, DailyLog

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'serving_size_grams', 'calories', 'protein', 'carbs', 'fat']

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['food', 'quantity_grams']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select'}),
            'quantity_grams': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade em gramas'}),
        }
        labels = {
            'food': 'Alimento',
            'quantity_grams': 'Quantidade (g)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['food'].queryset = Food.objects.filter(user=user)