# Generated migration to initialize workout exercises for existing active sessions

from django.db import migrations


def initialize_workout_exercises(apps, schema_editor):
    WorkoutSession = apps.get_model("logbook", "WorkoutSession")
    WorkoutExercise = apps.get_model("logbook", "WorkoutExercise")
    RoutineExercise = apps.get_model("logbook", "RoutineExercise")

    active_sessions = WorkoutSession.objects.filter(status="active")

    for session in active_sessions:
        if not WorkoutExercise.objects.filter(workout_session=session).exists():
            routine_exercises = RoutineExercise.objects.filter(routine=session.routine)

            for routine_exercise in routine_exercises:
                WorkoutExercise.objects.create(
                    workout_session=session,
                    exercise=routine_exercise.exercise,
                    order=routine_exercise.order,
                    sets=routine_exercise.sets,
                )


def reverse_initialize_workout_exercises(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("logbook", "0005_workoutexercise"),
    ]

    operations = [
        migrations.RunPython(
            initialize_workout_exercises, reverse_initialize_workout_exercises
        ),
    ]
