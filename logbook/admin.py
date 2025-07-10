from django.contrib import admin
from .models import (
    Exercise,
    Routine,
    RoutineExercise,
    WorkoutSession,
    SetLog,
    WorkoutExercise,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "description"]
    list_filter = ["user"]
    search_fields = ["name", "description"]


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created_at"]
    list_filter = ["user", "created_at"]
    search_fields = ["name", "user__username"]


@admin.register(RoutineExercise)
class RoutineExerciseAdmin(admin.ModelAdmin):
    list_display = ["routine", "exercise", "order", "sets"]
    list_filter = ["routine__user"]
    search_fields = ["routine__name", "exercise__name"]


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "routine", "date", "status", "start_time", "end_time"]
    list_filter = ["user", "status", "date"]
    search_fields = ["user__username", "routine__name"]


@admin.register(SetLog)
class SetLogAdmin(admin.ModelAdmin):
    list_display = ["workout_session", "exercise", "set_number", "weight", "reps"]
    list_filter = ["workout_session__user", "exercise"]
    search_fields = ["exercise__name", "workout_session__user__username"]


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ["workout_session", "exercise", "order", "sets"]
    list_filter = ["workout_session__user"]
    search_fields = ["exercise__name", "workout_session__user__username"]
