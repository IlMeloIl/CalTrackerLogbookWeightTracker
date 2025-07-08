from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Routine, Exercise, RoutineExercise
from .forms import RoutineForm, ExerciseForm, RoutineExerciseForm

class RoutineListView(LoginRequiredMixin, ListView):
    model = Routine
    template_name = 'logbook/routine_list.html'
    context_object_name = 'routines'
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

class RoutineCreateView(LoginRequiredMixin, CreateView):
    model = Routine
    form_class = RoutineForm
    template_name = 'logbook/routine_form.html'
    success_url = reverse_lazy('logbook:routine_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RoutineUpdateView(LoginRequiredMixin, UpdateView):
    model = Routine
    form_class = RoutineForm
    template_name = 'logbook/routine_form.html'
    success_url = reverse_lazy('logbook:routine_list')
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

class RoutineDeleteView(LoginRequiredMixin, DeleteView):
    model = Routine
    template_name = 'logbook/routine_confirm_delete.html'
    success_url = reverse_lazy('logbook:routine_list')
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'logbook/exercise_list.html'
    context_object_name = 'exercises'
    
    def get_queryset(self):
        return Exercise.objects.filter(
            models.Q(user=self.request.user) | models.Q(user=None)
        )

class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'logbook/exercise_form.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'logbook/exercise_form.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)

class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = 'logbook/exercise_confirm_delete.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)