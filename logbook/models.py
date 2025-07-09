from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q

User = get_user_model()

class Exercise(models.Model):
    name = models.CharField(max_length=100, help_text="Nome do exercício")
    description = models.TextField(blank=True, help_text="Descrição do exercício")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises', null=True, blank=True, help_text="Usuário criador (deixe vazio para exercícios globais)")
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user'],
                name='unique_exercise_per_user'
            ),
        ]
    
    def clean(self):
        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 2:
                raise ValidationError("Nome do exercício deve ter pelo menos 2 caracteres.")
    
    def __str__(self):
        return self.name

class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    name = models.CharField(max_length=100, help_text="Nome da rotina")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'user'],
                name='unique_routine_per_user'
            ),
        ]
    
    def clean(self):
        if self.name:
            self.name = self.name.strip()
            if len(self.name) < 2:
                raise ValidationError("Nome da rotina deve ter pelo menos 2 caracteres.")
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def can_start_workout(self):
        """Verifica se a rotina pode ser usada para iniciar um treino"""
        return self.routine_exercises.exists()
    
    def get_total_planned_sets(self):
        """Retorna o total de séries planejadas na rotina"""
        return sum(re.sets for re in self.routine_exercises.all())

class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='routine_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(help_text="Ordem do exercício na rotina")
    sets = models.PositiveIntegerField(help_text="Número de séries planejadas")
    
    class Meta:
        ordering = ['order']
        unique_together = ['routine', 'exercise']
    
    def clean(self):
        if self.sets and (self.sets < 1 or self.sets > 20):
            raise ValidationError("Número de séries deve estar entre 1 e 20.")
    
    def __str__(self):
        return f"{self.routine.name} - {self.exercise.name} ({self.sets} séries)"

class WorkoutSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
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
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(status='active'),
                name='unique_active_session_per_user'
            ),
        ]
    
    def clean(self):
        # Validar que não há outra sessão ativa para o mesmo usuário
        if self.status == 'active' and self.user_id:
            existing_active = WorkoutSession.objects.filter(
                user=self.user,
                status='active'
            ).exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError("Você já tem uma sessão de treino ativa.")
        
        # Validar que end_time é após start_time
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError("Hora de fim deve ser posterior à hora de início.")
    
    def __str__(self):
        return f"{self.user.username} - {self.routine.name} ({self.date})"
    
    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_exercise_logs(self):
        """Retorna os logs organizados por exercício"""
        exercises = {}
        for set_log in self.set_logs.all():
            if set_log.exercise not in exercises:
                exercises[set_log.exercise] = []
            exercises[set_log.exercise].append(set_log)
        return exercises
    
    def get_completion_percentage(self):
        """Calcula a porcentagem de conclusão do treino"""
        total_planned = self.routine.get_total_planned_sets()
        if total_planned == 0:
            return 0
        completed = self.set_logs.count()
        return min(100, (completed / total_planned) * 100)

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
    
    def clean(self):
        if self.weight is not None and (self.weight < 0 or self.weight > 1000):
            raise ValidationError("Peso deve estar entre 0 e 1000 kg.")
        
        if self.reps is not None and (self.reps < 1 or self.reps > 1000):
            raise ValidationError("Número de repetições deve estar entre 1 e 1000.")
        
        if self.set_number is not None and (self.set_number < 1 or self.set_number > 20):
            raise ValidationError("Número da série deve estar entre 1 e 20.")
    
    def __str__(self):
        return f"{self.exercise.name} - Série {self.set_number}: {self.weight}kg x {self.reps} reps"