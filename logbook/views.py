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
from django.utils import timezone
from datetime import date
from .models import Routine, Exercise, RoutineExercise, WorkoutSession, SetLog
from .forms import RoutineForm, ExerciseForm, RoutineExerciseForm, WorkoutSessionForm, SetLogForm

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

class StartWorkoutView(LoginRequiredMixin, View):
    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        
        # Verificar se há uma sessão ativa
        active_session = WorkoutSession.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if active_session:
            messages.warning(request, 'Você já tem um treino ativo. Finalize-o antes de iniciar outro.')
            return redirect('logbook:workout_session', pk=active_session.pk)
        
        # Verificar se a rotina tem exercícios
        if not routine.routine_exercises.exists():
            messages.error(request, 'Esta rotina não possui exercícios. Adicione exercícios antes de iniciar o treino.')
            return redirect('logbook:routine_detail', pk=routine_id)
        
        # Criar nova sessão de treino
        workout_session = WorkoutSession.objects.create(
            user=request.user,
            routine=routine,
            date=date.today()
        )
        
        messages.success(request, f'Treino "{routine.name}" iniciado!')
        return redirect('logbook:workout_session', pk=workout_session.pk)

class WorkoutSessionView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = 'logbook/workout_session.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Organizar exercícios da rotina com logs existentes
        exercises_data = []
        for routine_exercise in session.routine.routine_exercises.all():
            exercise = routine_exercise.exercise
            
            # Buscar logs existentes para este exercício
            existing_logs = SetLog.objects.filter(
                workout_session=session,
                exercise=exercise
            ).order_by('set_number')
            
            # Criar formulários para cada série planejada
            forms = []
            for set_num in range(1, routine_exercise.sets + 1):
                existing_log = existing_logs.filter(set_number=set_num).first()
                
                if existing_log:
                    form = SetLogForm(instance=existing_log)
                else:
                    form = SetLogForm(initial={'set_number': set_num})
                
                forms.append({
                    'form': form,
                    'set_number': set_num,
                    'existing_log': existing_log
                })
            
            exercises_data.append({
                'exercise': exercise,
                'routine_exercise': routine_exercise,
                'forms': forms,
                'existing_logs': existing_logs
            })
        
        context['exercises_data'] = exercises_data
        context['session_form'] = WorkoutSessionForm(instance=session)
        return context

class LogSetView(LoginRequiredMixin, View):
    def post(self, request, session_id, exercise_id, set_number):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        exercise = get_object_or_404(Exercise, id=exercise_id)
        
        if session.status != 'active':
            return JsonResponse({'success': False, 'error': 'Sessão não está ativa'})
        
        # Verificar se o exercício está na rotina
        if not RoutineExercise.objects.filter(routine=session.routine, exercise=exercise).exists():
            return JsonResponse({'success': False, 'error': 'Exercício não está na rotina'})
        
        # Buscar ou criar o log da série
        set_log, created = SetLog.objects.get_or_create(
            workout_session=session,
            exercise=exercise,
            set_number=set_number,
            defaults={'weight': 0, 'reps': 0}
        )
        
        form = SetLogForm(request.POST, instance=set_log)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'weight': str(set_log.weight),
                'reps': set_log.reps,
                'volume': str(set_log.volume)
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

class CompleteWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        
        if session.status != 'active':
            messages.error(request, 'Esta sessão não está ativa.')
            return redirect('logbook:routine_list')
        
        # Atualizar notas se fornecidas
        session_form = WorkoutSessionForm(request.POST, instance=session)
        if session_form.is_valid():
            session_form.save()
        
        # Marcar sessão como concluída
        session.status = 'completed'
        session.end_time = timezone.now()
        session.save()
        
        messages.success(request, f'Treino "{session.routine.name}" concluído!')
        return redirect('logbook:workout_history')

class CancelWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        
        if session.status != 'active':
            messages.error(request, 'Esta sessão não está ativa.')
            return redirect('logbook:routine_list')
        
        session.status = 'cancelled'
        session.end_time = timezone.now()
        session.save()
        
        messages.warning(request, f'Treino "{session.routine.name}" cancelado.')
        return redirect('logbook:routine_list')

class WorkoutHistoryView(LoginRequiredMixin, ListView):
    model = WorkoutSession
    template_name = 'logbook/workout_history.html'
    context_object_name = 'sessions'
    paginate_by = 10
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(
            user=self.request.user,
            status__in=['completed', 'cancelled']
        ).order_by('-date', '-start_time')

class WorkoutSessionDetailView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = 'logbook/workout_session_detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['exercise_logs'] = self.object.get_exercise_logs()
        
        total_volume = sum(log.volume for log in self.object.set_logs.all())
        context['total_volume'] = total_volume
        
        return context