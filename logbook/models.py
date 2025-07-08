from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Exercise(models.Model):
    name = models.CharField(max_length=100, help_text="Nome do exercício")
    description = models.TextField(blank=True, help_text="Descrição do exercício")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises', null=True, blank=True, help_text="Usuário criador (deixe vazio para exercícios globais)")
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    name = models.CharField(max_length=100, help_text="Nome da rotina")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"

class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='routine_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(help_text="Ordem do exercício na rotina")
    sets = models.PositiveIntegerField(help_text="Número de séries planejadas")
    
    class Meta:
        ordering = ['order']
        unique_together = ['routine', 'exercise']
    
    def __str__(self):
        return f"{self.routine.name} - {self.exercise.name} ({self.sets} séries)"