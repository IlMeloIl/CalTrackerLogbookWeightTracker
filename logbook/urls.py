from django.urls import path
from . import views

app_name = 'logbook'

urlpatterns = [
    path('', views.RoutineListView.as_view(), name='routine_list'),
    path('rotinas/add/', views.RoutineCreateView.as_view(), name='routine_add'),
    path('rotinas/<int:pk>/edit/', views.RoutineUpdateView.as_view(), name='routine_edit'),
    path('rotinas/<int:pk>/delete/', views.RoutineDeleteView.as_view(), name='routine_delete'),
    path('exercicios/', views.ExerciseListView.as_view(), name='exercise_list'),
    path('exercicios/add/', views.ExerciseCreateView.as_view(), name='exercise_add'),
    path('exercicios/<int:pk>/edit/', views.ExerciseUpdateView.as_view(), name='exercise_edit'),
    path('exercicios/<int:pk>/delete/', views.ExerciseDeleteView.as_view(), name='exercise_delete'),
]