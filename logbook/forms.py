from django import forms
from .models import Routine, Exercise, RoutineExercise

class RoutineForm(forms.ModelForm):
    class Meta:
        model = Routine
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da rotina'}),
        }
        labels = {
            'name': 'Nome da Rotina',
        }

class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do exercício'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descrição opcional'}),
        }
        labels = {
            'name': 'Nome do Exercício',
            'description': 'Descrição',
        }

class RoutineExerciseForm(forms.ModelForm):
    class Meta:
        model = RoutineExercise
        fields = ['exercise', 'sets']
        widgets = {
            'exercise': forms.Select(attrs={'class': 'form-select'}),
            'sets': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
        }
        labels = {
            'exercise': 'Exercício',
            'sets': 'Número de Séries',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['exercise'].queryset = Exercise.objects.filter(
                models.Q(user=user) | models.Q(user=None)
            )