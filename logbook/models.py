from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

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

class WorkoutSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_sessions')
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True, help_text="Notas sobre o treino")
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.routine.name} ({self.date})"
    
    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_exercise_logs(self):
        exercises = {}
        for set_log in self.set_logs.all():
            if set_log.exercise not in exercises:
                exercises[set_log.exercise] = []
            exercises[set_log.exercise].append(set_log)
        return exercises

class SetLog(models.Model):
    workout_session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='set_logs')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField(help_text="Número da série")
    weight = models.DecimalField(max_digits=6, decimal_places=2, help_text="Peso utilizado (kg)")
    reps = models.PositiveIntegerField(help_text="Número de repetições")
    notes = models.TextField(blank=True, help_text="Notas sobre esta série")
    
    class Meta:
        ordering = ['exercise', 'set_number']
        unique_together = ['workout_session', 'exercise', 'set_number']
    
    def __str__(self):
        return f"{self.exercise.name} - Série {self.set_number}: {self.weight}kg x {self.reps} reps"
    
    @property
    def volume(self):
        return self.weight * self.reps