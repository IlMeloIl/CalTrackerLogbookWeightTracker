from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
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
from datetime import date, timedelta
from .models import Routine, Exercise, RoutineExercise, WorkoutSession, SetLog
from .forms import RoutineForm, ExerciseForm, RoutineExerciseForm, WorkoutSessionForm, SetLogForm
from django.db.models import Count, Sum, Q


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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Rotina "{form.instance.name}" criada com sucesso!')
            return response
        except IntegrityError:
            messages.error(self.request, 'Você já tem uma rotina com este nome.')
            return self.form_invalid(form)

class RoutineUpdateView(LoginRequiredMixin, UpdateView):
    model = Routine
    form_class = RoutineForm
    template_name = 'logbook/routine_form.html'
    success_url = reverse_lazy('logbook:routine_list')
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Rotina "{form.instance.name}" atualizada com sucesso!')
            return response
        except IntegrityError:
            messages.error(self.request, 'Você já tem uma rotina com este nome.')
            return self.form_invalid(form)

class RoutineDeleteView(LoginRequiredMixin, DeleteView):
    model = Routine
    template_name = 'logbook/routine_confirm_delete.html'
    success_url = reverse_lazy('logbook:routine_list')
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar se há treinos ativos usando esta rotina
        active_sessions = WorkoutSession.objects.filter(
            routine=self.object,
            status='active'
        )
        
        if active_sessions.exists():
            messages.error(request, 'Não é possível excluir uma rotina com treinos ativos.')
            return redirect('logbook:routine_detail', pk=self.object.pk)
        
        routine_name = self.object.name
        messages.success(request, f'Rotina "{routine_name}" excluída com sucesso!')
        return super().delete(request, *args, **kwargs)

class RoutineDetailView(LoginRequiredMixin, DetailView):
    model = Routine
    template_name = 'logbook/routine_detail.html'
    context_object_name = 'routine'
    
    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['routine_exercises'] = self.object.routine_exercises.all()
        context['form'] = RoutineExerciseForm(user=self.request.user, routine=self.object)
        return context

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'logbook/exercise_list.html'
    context_object_name = 'exercises'
    
    def get_queryset(self):
        # Inclui exercícios globais (user=None) e do usuário
        return Exercise.objects.filter(
            models.Q(user=self.request.user) | models.Q(user=None)
        ).order_by('-user', 'name')

class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'logbook/exercise_form.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, f'Exercício "{form.instance.name}" criado com sucesso!')
            return response
        except IntegrityError:
            messages.error(self.request, 'Você já tem um exercício com este nome.')
            return self.form_invalid(form)

class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = 'logbook/exercise_form.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def get_queryset(self):
        # Só permite editar exercícios do próprio usuário
        return Exercise.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'Exercício "{form.instance.name}" atualizado com sucesso!')
            return response
        except IntegrityError:
            messages.error(self.request, 'Você já tem um exercício com este nome.')
            return self.form_invalid(form)

class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = 'logbook/exercise_confirm_delete.html'
    success_url = reverse_lazy('logbook:exercise_list')
    
    def get_queryset(self):
        # Só permite deletar exercícios do próprio usuário
        return Exercise.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Verificar se o exercício está sendo usado em alguma rotina
        routine_uses = RoutineExercise.objects.filter(
            exercise=self.object,
            routine__user=request.user
        )
        
        if routine_uses.exists():
            routine_names = [ru.routine.name for ru in routine_uses[:3]]
            if len(routine_uses) > 3:
                routine_names.append('...')
            
            messages.error(
                request, 
                f'Não é possível excluir este exercício. Ele está sendo usado nas rotinas: {", ".join(routine_names)}'
            )
            return redirect('logbook:exercise_list')
        
        exercise_name = self.object.name
        messages.success(request, f'Exercício "{exercise_name}" excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

class AddExerciseToRoutineView(LoginRequiredMixin, View):
    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        form = RoutineExerciseForm(request.POST, user=request.user, routine=routine)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    routine_exercise = form.save(commit=False)
                    routine_exercise.routine = routine
                    
                    # Definir a ordem como o próximo número disponível
                    last_order = routine.routine_exercises.aggregate(
                        models.Max('order')
                    )['order__max'] or 0
                    routine_exercise.order = last_order + 1
                    
                    routine_exercise.save()
                    messages.success(request, f'Exercício "{routine_exercise.exercise.name}" adicionado à rotina!')
            except IntegrityError:
                messages.error(request, 'Este exercício já está na rotina.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        
        return redirect('logbook:routine_detail', pk=routine_id)

class RemoveExerciseFromRoutineView(LoginRequiredMixin, View):
    def post(self, request, routine_id, exercise_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)
        
        try:
            routine_exercise = RoutineExercise.objects.get(
                routine=routine,
                exercise_id=exercise_id
            )
            exercise_name = routine_exercise.exercise.name
            routine_exercise.delete()
            
            # Reordenar os exercícios restantes
            remaining_exercises = routine.routine_exercises.order_by('order')
            for i, re in enumerate(remaining_exercises, 1):
                if re.order != i:
                    re.order = i
                    re.save()
            
            messages.success(request, f'Exercício "{exercise_name}" removido da rotina!')
        except RoutineExercise.DoesNotExist:
            messages.error(request, 'Exercício não encontrado na rotina.')
        
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
        if not routine.can_start_workout():
            messages.error(request, 'Esta rotina não possui exercícios. Adicione exercícios antes de iniciar o treino.')
            return redirect('logbook:routine_detail', pk=routine_id)
        
        try:
            # Criar nova sessão de treino
            workout_session = WorkoutSession.objects.create(
                user=request.user,
                routine=routine,
                date=date.today()
            )
            
            messages.success(request, f'Treino "{routine.name}" iniciado!')
            return redirect('logbook:workout_session', pk=workout_session.pk)
        except IntegrityError:
            messages.error(request, 'Erro ao iniciar treino. Tente novamente.')
            return redirect('logbook:routine_detail', pk=routine_id)

class WorkoutSessionView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = 'logbook/workout_session.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Verificar se a sessão ainda está ativa
        if session.status != 'active':
            messages.warning(self.request, 'Esta sessão de treino não está mais ativa.')
        
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
        
        # Validações de segurança
        if session.status != 'active':
            return JsonResponse({'success': False, 'error': 'Sessão não está ativa'})
        
        # Verificar se o exercício está na rotina
        if not RoutineExercise.objects.filter(routine=session.routine, exercise=exercise).exists():
            return JsonResponse({'success': False, 'error': 'Exercício não está na rotina'})
        
        # Verificar se o número da série é válido
        routine_exercise = RoutineExercise.objects.get(routine=session.routine, exercise=exercise)
        if set_number < 1 or set_number > routine_exercise.sets:
            return JsonResponse({'success': False, 'error': 'Número de série inválido'})
        
        try:
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
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class CompleteWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        
        if session.status != 'active':
            messages.error(request, 'Esta sessão não está ativa.')
            return redirect('logbook:routine_list')
        
        try:
            with transaction.atomic():
                # Atualizar notas se fornecidas
                session_form = WorkoutSessionForm(request.POST, instance=session)
                if session_form.is_valid():
                    session_form.save()
                
                # Marcar sessão como concluída
                session.status = 'completed'
                session.end_time = timezone.now()
                session.save()
                
                messages.success(request, f'Treino "{session.routine.name}" concluído com sucesso!')
                return redirect('logbook:workout_history')
        except Exception as e:
            messages.error(request, f'Erro ao concluir treino: {str(e)}')
            return redirect('logbook:workout_session', pk=session_id)

class CancelWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        
        if session.status != 'active':
            messages.error(request, 'Esta sessão não está ativa.')
            return redirect('logbook:routine_list')
        
        try:
            with transaction.atomic():
                session.status = 'cancelled'
                session.end_time = timezone.now()
                session.save()
                
                messages.warning(request, f'Treino "{session.routine.name}" cancelado.')
                return redirect('logbook:routine_list')
        except Exception as e:
            messages.error(request, f'Erro ao cancelar treino: {str(e)}')
            return redirect('logbook:workout_session', pk=session_id)

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'logbook/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        try:
            # Estatísticas gerais
            total_sessions = WorkoutSession.objects.filter(user=user, status='completed').count()
            total_routines = Routine.objects.filter(user=user).count()
            total_exercises = Exercise.objects.filter(user=user).count()
            
            # Sessão ativa
            active_session = WorkoutSession.objects.filter(user=user, status='active').first()
            
            # Estatísticas dos últimos 30 dias
            thirty_days_ago = date.today() - timedelta(days=30)
            recent_stats = WorkoutSession.objects.filter(
                user=user,
                status='completed',
                date__gte=thirty_days_ago
            ).aggregate(
                total_sessions=Count('id'),
                total_sets=Count('set_logs')
            )
            
            # Rotinas mais usadas
            popular_routines = Routine.objects.filter(
                user=user
            ).annotate(
                session_count=Count('workoutsession', filter=Q(workoutsession__status='completed'))
            ).order_by('-session_count')[:5]
            
            # Volume por exercício (top 5)
            top_exercises = Exercise.objects.filter(
                setlog__workout_session__user=user,
                setlog__workout_session__status='completed'
            ).annotate(
                total_volume=Sum(
                    models.F('setlog__weight') * models.F('setlog__reps'),
                    output_field=models.DecimalField()
                )
            ).order_by('-total_volume')[:5]
            
            context.update({
                'total_sessions': total_sessions,
                'total_routines': total_routines,
                'total_exercises': total_exercises,
                'active_session': active_session,
                'recent_stats': recent_stats,
                'popular_routines': popular_routines,
                'top_exercises': top_exercises,
            })
        except Exception as e:
            messages.error(self.request, f'Erro ao carregar dashboard: {str(e)}')
            context.update({
                'total_sessions': 0,
                'total_routines': 0,
                'total_exercises': 0,
                'active_session': None,
                'recent_stats': {'total_sessions': 0, 'total_sets': 0},
                'popular_routines': [],
                'top_exercises': [],
            })
        
        return context

class ExerciseProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'logbook/exercise_progress.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Obter exercícios personalizados do usuário
        user_exercises = Exercise.objects.filter(user=user).order_by('name')
        
        # Parâmetros da URL
        exercise_id = self.request.GET.get('exercise')
        period = self.request.GET.get('period', '90')  # 90 dias por padrão
        
        selected_exercise = None
        stats = None
        chart_data = None
        recent_sets = None
        
        if exercise_id:
            try:
                selected_exercise = Exercise.objects.get(id=exercise_id, user=user)
                
                # Calcular período
                days_ago = int(period)
                start_date = date.today() - timedelta(days=days_ago)
                
                # Buscar dados do exercício
                set_logs = SetLog.objects.filter(
                    exercise=selected_exercise,
                    workout_session__user=user,
                    workout_session__status='completed',
                    workout_session__date__gte=start_date
                ).order_by('workout_session__date', 'set_number')
                
                if set_logs.exists():
                    # Calcular estatísticas
                    stats = {
                        'total_workouts': set_logs.values('workout_session').distinct().count(),
                        'total_sets': set_logs.count(),
                        'max_weight': set_logs.aggregate(models.Max('weight'))['weight__max'] or 0,
                        'total_volume': sum(log.volume for log in set_logs),
                    }
                    
                    # Preparar dados para o gráfico
                    chart_data = self._prepare_chart_data(set_logs)
                    
                    # Últimas 20 séries
                    recent_sets = set_logs.order_by('-workout_session__date', '-set_number')[:20]
                else:
                    stats = {
                        'total_workouts': 0,
                        'total_sets': 0,
                        'max_weight': 0,
                        'total_volume': 0,
                    }
                    
            except (Exercise.DoesNotExist, ValueError):
                pass
        
        context.update({
            'user_exercises': user_exercises,
            'selected_exercise': selected_exercise,
            'period': period,
            'stats': stats,
            'chart_data': chart_data,
            'recent_sets': recent_sets,
        })
        
        return context
    
    def _prepare_chart_data(self, set_logs):
        """Prepara dados para o gráfico de progresso"""
        import json
        
        # Agrupar por data de treino e calcular peso máximo por treino
        workout_data = {}
        for log in set_logs:
            workout_date = log.workout_session.date
            if workout_date not in workout_data:
                workout_data[workout_date] = {
                    'max_weight': float(log.weight),
                    'avg_weight': [],
                    'total_volume': 0
                }
            else:
                workout_data[workout_date]['max_weight'] = max(
                    workout_data[workout_date]['max_weight'], 
                    float(log.weight)
                )
            
            workout_data[workout_date]['avg_weight'].append(float(log.weight))
            workout_data[workout_date]['total_volume'] += float(log.volume)
        
        # Calcular peso médio por treino
        for date_key in workout_data:
            weights = workout_data[date_key]['avg_weight']
            workout_data[date_key]['avg_weight'] = sum(weights) / len(weights)
        
        # Ordenar por data
        sorted_dates = sorted(workout_data.keys())
        
        # Preparar dados para Chart.js
        labels = [date.strftime('%d/%m') for date in sorted_dates]
        max_weights = [workout_data[date]['max_weight'] for date in sorted_dates]
        avg_weights = [workout_data[date]['avg_weight'] for date in sorted_dates]
        volumes = [workout_data[date]['total_volume'] for date in sorted_dates]
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Peso Máximo',
                    'data': max_weights,
                    'borderColor': '#dc3545',
                    'backgroundColor': 'rgba(220, 53, 69, 0.1)',
                    'tension': 0.3,
                    'fill': False,
                    'pointRadius': 5,
                    'pointHoverRadius': 8,
                },
                {
                    'label': 'Peso Médio',
                    'data': avg_weights,
                    'borderColor': '#0d6efd',
                    'backgroundColor': 'rgba(13, 110, 253, 0.1)',
                    'tension': 0.3,
                    'fill': False,
                    'pointRadius': 4,
                    'pointHoverRadius': 6,
                }
            ]
        }
        
        return json.dumps(chart_data)