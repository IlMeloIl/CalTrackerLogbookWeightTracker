from django.contrib import admin
from .models import (
    Exercise,
    Routine,
    RoutineExercise,
    WorkoutSession,
    SetLog,
    WorkoutExercise,
)

admin.site.register(Exercise)
admin.site.register(Routine)
admin.site.register(RoutineExercise)
admin.site.register(WorkoutSession)
admin.site.register(SetLog)
admin.site.register(WorkoutExercise)
