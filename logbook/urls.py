from django.urls import path
from . import views

app_name = "logbook"

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("", views.RoutineListView.as_view(), name="routine_list"),
    path("rotinas/add/", views.RoutineCreateView.as_view(), name="routine_add"),
    path("rotinas/<int:pk>/", views.RoutineDetailView.as_view(), name="routine_detail"),
    path(
        "rotinas/<int:pk>/edit/", views.RoutineUpdateView.as_view(), name="routine_edit"
    ),
    path(
        "rotinas/<int:pk>/delete/",
        views.RoutineDeleteView.as_view(),
        name="routine_delete",
    ),
    path(
        "rotinas/<int:pk>/delete-ajax/",
        views.RoutineDeleteAjaxView.as_view(),
        name="routine_delete_ajax",
    ),
    path(
        "rotinas/<int:pk>/edit-ajax/",
        views.RoutineUpdateAjaxView.as_view(),
        name="routine_edit_ajax",
    ),
    path(
        "rotinas/<int:routine_id>/add-exercise/",
        views.AddExerciseToRoutineView.as_view(),
        name="add_exercise_to_routine",
    ),
    path(
        "rotinas/<int:routine_id>/remove-exercise/<int:exercise_id>/",
        views.RemoveExerciseFromRoutineView.as_view(),
        name="remove_exercise_from_routine",
    ),
    path(
        "rotinas/<int:routine_id>/reorder/",
        views.ReorderExercisesView.as_view(),
        name="reorder_exercises",
    ),
    path(
        "rotina/<int:routine_id>/start/",
        views.StartWorkoutView.as_view(),
        name="start_workout",
    ),
    path(
        "treino/<int:pk>/", views.WorkoutSessionView.as_view(), name="workout_session"
    ),
    path(
        "treino/<int:session_id>/log/<int:exercise_id>/<int:set_number>/",
        views.LogSetView.as_view(),
        name="log_set",
    ),
    path(
        "treino/<int:session_id>/complete/",
        views.CompleteWorkoutView.as_view(),
        name="complete_workout",
    ),
    path(
        "treino/<int:session_id>/cancel/",
        views.CancelWorkoutView.as_view(),
        name="cancel_workout",
    ),
    path(
        "treino/<int:session_id>/reorder-exercises/",
        views.ReorderWorkoutExercisesView.as_view(),
        name="reorder_workout_exercises",
    ),
    path(
        "treino/<int:session_id>/add-exercise/",
        views.AddExerciseToWorkoutView.as_view(),
        name="add_exercise_to_workout",
    ),
    path(
        "treino/<int:session_id>/remove-exercise/<int:exercise_id>/",
        views.RemoveExerciseFromWorkoutView.as_view(),
        name="remove_exercise_from_workout",
    ),
    path(
        "treino/<int:session_id>/update-sets/<int:exercise_id>/",
        views.UpdateWorkoutExerciseSetsView.as_view(),
        name="update_workout_exercise_sets",
    ),
    path("exercicios/", views.ExerciseListView.as_view(), name="exercise_list"),
    path("exercicios/add/", views.ExerciseCreateView.as_view(), name="exercise_add"),
    path(
        "exercicios/<int:pk>/edit/",
        views.ExerciseUpdateView.as_view(),
        name="exercise_edit",
    ),
    path(
        "exercicios/<int:pk>/delete/",
        views.ExerciseDeleteView.as_view(),
        name="exercise_delete",
    ),
    path(
        "exercicios/<int:pk>/delete-ajax/",
        views.ExerciseDeleteAjaxView.as_view(),
        name="exercise_delete_ajax",
    ),
    path(
        "exercicios/<int:pk>/edit-ajax/",
        views.ExerciseUpdateAjaxView.as_view(),
        name="exercise_edit_ajax",
    ),
    path("progresso/", views.ExerciseProgressView.as_view(), name="exercise_progress"),
]
