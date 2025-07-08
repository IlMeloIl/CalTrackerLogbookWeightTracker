from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.db import models
from .models import Routine, Exercise, RoutineExercise
from .forms import RoutineForm, ExerciseForm, RoutineExerciseForm
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.db import models, transaction

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

class RoutineDetailView(LoginRequiredMixin, DetailView):
    model = Routine
    template_name = 'logbook/routine_detail.html'
    context_object_name = 'routine'
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routine_exercises'] = self.object.routine_exercises.all()
        context['form'] = RoutineExerciseForm(user=self.request.user)
        return context

class AddExerciseToRoutineView(LoginRequiredMixin, View):
    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        form = RoutineExerciseForm(request.POST, user=request.user)
        
        if form.is_valid():
            # Verificar se o exercício já está na rotina
            exercise = form.cleaned_data['exercise']
            if RoutineExercise.objects.filter(routine=routine, exercise=exercise).exists():
                messages.error(request, f'O exercício "{exercise.name}" já está nesta rotina.')
            else:
                # Definir a ordem como o próximo número
                max_order = RoutineExercise.objects.filter(routine=routine).aggregate(
                    models.Max('order')
                )['order__max'] or 0
                
                routine_exercise = form.save(commit=False)
                routine_exercise.routine = routine
                routine_exercise.order = max_order + 1
                routine_exercise.save()
                messages.success(request, f'Exercício "{exercise.name}" adicionado à rotina.')
        else:
            messages.error(request, 'Erro ao adicionar exercício. Verifique os dados.')
        
        return redirect('logbook:routine_detail', pk=routine_id)

class RemoveExerciseFromRoutineView(LoginRequiredMixin, View):
    def post(self, request, routine_id, exercise_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        routine_exercise = get_object_or_404(
            RoutineExercise, 
            routine=routine, 
            exercise_id=exercise_id
        )
        
        exercise_name = routine_exercise.exercise.name
        routine_exercise.delete()
        
        # Reordenar os exercícios restantes
        remaining_exercises = RoutineExercise.objects.filter(routine=routine).order_by('order')
        for i, re in enumerate(remaining_exercises, 1):
            re.order = i
            re.save()
        
        messages.success(request, f'Exercício "{exercise_name}" removido da rotina.')
        return redirect('logbook:routine_detail', pk=routine_id)

class ReorderExercisesView(LoginRequiredMixin, View):
    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        
        try:
            exercise_ids = request.POST.getlist('exercise_ids[]')
            
            with transaction.atomic():
                for i, exercise_id in enumerate(exercise_ids, 1):
                    RoutineExercise.objects.filter(
                        routine=routine,
                        exercise_id=exercise_id
                    ).update(order=i)
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})