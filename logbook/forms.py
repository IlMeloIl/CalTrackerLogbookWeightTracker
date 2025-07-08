from django import forms
from django.core.exceptions import ValidationError
from .models import Routine, Exercise, RoutineExercise, WorkoutSession, SetLog
from django.db import models
from datetime import date


class RoutineForm(forms.ModelForm):
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
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Nome deve ter pelo menos 2 caracteres.")

            if hasattr(self, "user"):
                existing = Routine.objects.filter(
                    name__iexact=name, user=self.user
                ).exclude(pk=self.instance.pk if self.instance else None)

                if existing.exists():
                    raise ValidationError("Você já tem uma rotina com este nome.")

        return name

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class ExerciseForm(forms.ModelForm):
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
        if name:
            name = name.strip()
            if len(name) < 2:
                raise ValidationError("Nome deve ter pelo menos 2 caracteres.")

            if hasattr(self, "user"):
                existing = Exercise.objects.filter(
                    name__iexact=name, user=self.user
                ).exclude(pk=self.instance.pk if self.instance else None)

                if existing.exists():
                    raise ValidationError("Você já tem um exercício com este nome.")

        return name

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
        if sets is not None and (sets < 1 or sets > 20):
            raise ValidationError("Número de séries deve estar entre 1 e 20.")
        return sets

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
        if weight is not None and (weight < 0 or weight > 1000):
            raise ValidationError("Peso deve estar entre 0 e 1000 kg.")
        return weight

    def clean_reps(self):
        reps = self.cleaned_data.get("reps")
        if reps is not None and (reps < 1 or reps > 1000):
            raise ValidationError("Número de repetições deve estar entre 1 e 1000.")
        return reps


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
