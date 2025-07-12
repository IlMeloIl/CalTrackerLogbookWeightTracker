from django import forms
from django.core.exceptions import ValidationError
from .models import Routine, Exercise, RoutineExercise, WorkoutSession, SetLog
from django.db import models
from datetime import date
from shared.utils import NumericValidatorMixin, UniqueNameValidatorMixin


class RoutineForm(UniqueNameValidatorMixin, forms.ModelForm):
    class Meta:
        model = Routine
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome da rotina"}
            ),
        }
        labels = {
            "name": "Nome da Rotina",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return self.validar_nome_unico(name)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class ExerciseForm(UniqueNameValidatorMixin, forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nome do exercício"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descrição opcional",
                }
            ),
        }
        labels = {
            "name": "Nome do Exercício",
            "description": "Descrição",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name")
        return self.validar_nome_unico(name)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class RoutineExerciseForm(forms.ModelForm):
    class Meta:
        model = RoutineExercise
        fields = ["exercise", "sets"]
        widgets = {
            "exercise": forms.Select(attrs={"class": "form-select"}),
            "sets": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 20}
            ),
        }
        labels = {
            "exercise": "Exercício",
            "sets": "Número de Séries",
        }

    def clean_sets(self):
        sets = self.cleaned_data.get("sets")
        return NumericValidatorMixin.validar_series(sets)

    def clean_exercise(self):
        exercise = self.cleaned_data.get("exercise")
        if exercise and hasattr(self, "routine"):
            existing = RoutineExercise.objects.filter(
                routine=self.routine, exercise=exercise
            ).exclude(pk=self.instance.pk if self.instance else None)

            if existing.exists():
                raise ValidationError("Este exercício já está na rotina.")

        return exercise

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        self.routine = kwargs.pop("routine", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["exercise"].queryset = Exercise.objects.filter(
                models.Q(user=user) | models.Q(user=None)
            )


class WorkoutSessionForm(forms.ModelForm):
    class Meta:
        model = WorkoutSession
        fields = ["notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Notas sobre o treino (opcional)",
                }
            ),
        }
        labels = {
            "notes": "Notas",
        }


class SetLogForm(forms.ModelForm):
    class Meta:
        model = SetLog
        fields = ["weight", "reps", "notes"]
        widgets = {
            "weight": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.5",
                    "min": "0",
                    "max": "1000",
                }
            ),
            "reps": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "max": "1000"}
            ),
            "notes": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Notas (opcional)"}
            ),
        }
        labels = {
            "weight": "Peso (kg)",
            "reps": "Repetições",
            "notes": "Notas",
        }

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        return NumericValidatorMixin.validar_peso(weight)

    def clean_reps(self):
        reps = self.cleaned_data.get("reps")
        return NumericValidatorMixin.validar_repeticoes(reps)


class StartWorkoutForm(forms.Form):
    date = forms.DateField(
        label="Data do Treino",
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
                "max": date.today().strftime("%Y-%m-%d"),
            }
        ),
        initial=date.today,
        help_text="Selecione a data do treino (não pode ser no futuro)",
    )

    def clean_date(self):
        workout_date = self.cleaned_data.get("date")
        if workout_date and workout_date > date.today():
            raise ValidationError("A data do treino não pode ser no futuro.")
        return workout_date
