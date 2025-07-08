from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
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
from .forms import (
    RoutineForm,
    ExerciseForm,
    RoutineExerciseForm,
    WorkoutSessionForm,
    SetLogForm,
    StartWorkoutForm,
)
import json


class RoutineListView(LoginRequiredMixin, ListView):
    model = Routine
    template_name = "logbook/routine_list.html"
    context_object_name = "routines"

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)


class RoutineCreateView(LoginRequiredMixin, CreateView):
    model = Routine
    form_class = RoutineForm
    template_name = "logbook/routine_form.html"
    success_url = reverse_lazy("logbook:routine_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(
                self.request, f'Rotina "{form.instance.name}" criada com sucesso!'
            )
            return response
        except IntegrityError:
            messages.error(self.request, "Você já tem uma rotina com este nome.")
            return self.form_invalid(form)


class RoutineUpdateView(LoginRequiredMixin, UpdateView):
    model = Routine
    form_class = RoutineForm
    template_name = "logbook/routine_form.html"
    success_url = reverse_lazy("logbook:routine_list")

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request, f'Rotina "{form.instance.name}" atualizada com sucesso!'
            )
            return response
        except IntegrityError:
            messages.error(self.request, "Você já tem uma rotina com este nome.")
            return self.form_invalid(form)


class RoutineDeleteView(LoginRequiredMixin, DeleteView):
    model = Routine
    template_name = "logbook/routine_confirm_delete.html"
    success_url = reverse_lazy("logbook:routine_list")

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        active_sessions = WorkoutSession.objects.filter(
            routine=self.object, status="active"
        )

        if active_sessions.exists():
            messages.error(
                request, "Não é possível excluir uma rotina com treinos ativos."
            )
            return redirect("logbook:routine_detail", pk=self.object.pk)

        routine_name = self.object.name
        messages.success(request, f'Rotina "{routine_name}" excluída com sucesso!')
        return super().delete(request, *args, **kwargs)


class RoutineDetailView(LoginRequiredMixin, DetailView):
    model = Routine
    template_name = "logbook/routine_detail.html"
    context_object_name = "routine"

    def get_queryset(self):
        return Routine.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["routine_exercises"] = self.object.routine_exercises.all()
        context["form"] = RoutineExerciseForm(
            user=self.request.user, routine=self.object
        )
        return context


class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = "logbook/exercise_list.html"
    context_object_name = "exercises"

    def get_queryset(self):

        return Exercise.objects.filter(
            models.Q(user=self.request.user) | models.Q(user=None)
        ).order_by("-user", "name")


class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = "logbook/exercise_form.html"
    success_url = reverse_lazy("logbook:exercise_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(
                self.request, f'Exercício "{form.instance.name}" criado com sucesso!'
            )
            return response
        except IntegrityError:
            messages.error(self.request, "Você já tem um exercício com este nome.")
            return self.form_invalid(form)


class ExerciseUpdateView(LoginRequiredMixin, UpdateView):
    model = Exercise
    form_class = ExerciseForm
    template_name = "logbook/exercise_form.html"
    success_url = reverse_lazy("logbook:exercise_list")

    def get_queryset(self):

        return Exercise.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(
                self.request,
                f'Exercício "{form.instance.name}" atualizado com sucesso!',
            )
            return response
        except IntegrityError:
            messages.error(self.request, "Você já tem um exercício com este nome.")
            return self.form_invalid(form)


class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = "logbook/exercise_confirm_delete.html"
    success_url = reverse_lazy("logbook:exercise_list")

    def get_queryset(self):

        return Exercise.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        routine_uses = RoutineExercise.objects.filter(
            exercise=self.object, routine__user=request.user
        )

        if routine_uses.exists():
            routine_names = [ru.routine.name for ru in routine_uses[:3]]
            if len(routine_uses) > 3:
                routine_names.append("...")

            messages.error(
                request,
                f'Não é possível excluir este exercício. Ele está sendo usado nas rotinas: {", ".join(routine_names)}',
            )
            return redirect("logbook:exercise_list")

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

                    last_order = (
                        routine.routine_exercises.aggregate(models.Max("order"))[
                            "order__max"
                        ]
                        or 0
                    )
                    routine_exercise.order = last_order + 1

                    routine_exercise.save()
                    messages.success(
                        request,
                        f'Exercício "{routine_exercise.exercise.name}" adicionado à rotina!',
                    )
            except IntegrityError:
                messages.error(request, "Este exercício já está na rotina.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)

        return redirect("logbook:routine_detail", pk=routine_id)


class RemoveExerciseFromRoutineView(LoginRequiredMixin, View):
    def post(self, request, routine_id, exercise_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)

        try:
            routine_exercise = RoutineExercise.objects.get(
                routine=routine, exercise_id=exercise_id
            )
            exercise_name = routine_exercise.exercise.name
            routine_exercise.delete()

            remaining_exercises = routine.routine_exercises.order_by("order")
            for i, re in enumerate(remaining_exercises, 1):
                if re.order != i:
                    re.order = i
                    re.save()

            messages.success(
                request, f'Exercício "{exercise_name}" removido da rotina!'
            )
        except RoutineExercise.DoesNotExist:
            messages.error(request, "Exercício não encontrado na rotina.")

        return redirect("logbook:routine_detail", pk=routine_id)


class ReorderExercisesView(LoginRequiredMixin, View):
    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)

        try:
            exercise_ids = request.POST.getlist("exercise_ids[]")

            with transaction.atomic():
                for i, exercise_id in enumerate(exercise_ids, 1):
                    RoutineExercise.objects.filter(
                        routine=routine, exercise_id=exercise_id
                    ).update(order=i)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class StartWorkoutView(LoginRequiredMixin, View):
    def get(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)

        active_session = WorkoutSession.objects.filter(
            user=request.user, status="active"
        ).first()

        if active_session:
            messages.warning(
                request,
                "Você já tem um treino ativo. Finalize-o antes de iniciar outro.",
            )
            return redirect("logbook:workout_session", pk=active_session.pk)

        if not routine.can_start_workout():
            messages.error(
                request,
                "Esta rotina não possui exercícios. Adicione exercícios antes de iniciar o treino.",
            )
            return redirect("logbook:routine_detail", pk=routine_id)

        form = StartWorkoutForm()
        return render(
            request, "logbook/start_workout.html", {"routine": routine, "form": form}
        )

    def post(self, request, routine_id):
        routine = get_object_or_404(Routine, id=routine_id, user=request.user)

        active_session = WorkoutSession.objects.filter(
            user=request.user, status="active"
        ).first()

        if active_session:
            messages.warning(
                request,
                "Você já tem um treino ativo. Finalize-o antes de iniciar outro.",
            )
            return redirect("logbook:workout_session", pk=active_session.pk)

        if not routine.can_start_workout():
            messages.error(
                request,
                "Esta rotina não possui exercícios. Adicione exercícios antes de iniciar o treino.",
            )
            return redirect("logbook:routine_detail", pk=routine_id)

        form = StartWorkoutForm(request.POST)
        if form.is_valid():
            workout_date = form.cleaned_data["date"]

            try:

                workout_session = WorkoutSession.objects.create(
                    user=request.user, routine=routine, date=workout_date
                )

                messages.success(
                    request,
                    f'Treino "{routine.name}" iniciado para {workout_date.strftime("%d/%m/%Y")}!',
                )
                return redirect("logbook:workout_session", pk=workout_session.pk)
            except IntegrityError:
                messages.error(request, "Erro ao iniciar treino. Tente novamente.")
                return redirect("logbook:routine_detail", pk=routine_id)

        return render(
            request, "logbook/start_workout.html", {"routine": routine, "form": form}
        )


class WorkoutSessionView(LoginRequiredMixin, DetailView):
    model = WorkoutSession
    template_name = "logbook/workout_session.html"
    context_object_name = "session"

    def get_queryset(self):
        return WorkoutSession.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object

        if session.status != "active":
            messages.warning(self.request, "Esta sessão de treino não está mais ativa.")

        exercises_data = []
        for routine_exercise in session.routine.routine_exercises.all():
            exercise = routine_exercise.exercise

            existing_logs = SetLog.objects.filter(
                workout_session=session, exercise=exercise
            ).order_by("set_number")

            forms = []
            for set_num in range(1, routine_exercise.sets + 1):
                existing_log = existing_logs.filter(set_number=set_num).first()

                if existing_log:
                    form = SetLogForm(instance=existing_log)
                else:
                    form = SetLogForm(initial={"set_number": set_num})

                forms.append(
                    {"form": form, "set_number": set_num, "existing_log": existing_log}
                )

            exercises_data.append(
                {
                    "exercise": exercise,
                    "routine_exercise": routine_exercise,
                    "forms": forms,
                    "existing_logs": existing_logs,
                }
            )

        context["exercises_data"] = exercises_data
        context["session_form"] = WorkoutSessionForm(instance=session)
        return context


class LogSetView(LoginRequiredMixin, View):
    def post(self, request, session_id, exercise_id, set_number):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
        exercise = get_object_or_404(Exercise, id=exercise_id)

        if session.status != "active":
            return JsonResponse({"success": False, "error": "Sessão não está ativa"})

        if not RoutineExercise.objects.filter(
            routine=session.routine, exercise=exercise
        ).exists():
            return JsonResponse(
                {"success": False, "error": "Exercício não está na rotina"}
            )

        routine_exercise = RoutineExercise.objects.get(
            routine=session.routine, exercise=exercise
        )
        if set_number < 1 or set_number > routine_exercise.sets:
            return JsonResponse({"success": False, "error": "Número de série inválido"})

        try:

            set_log, created = SetLog.objects.get_or_create(
                workout_session=session,
                exercise=exercise,
                set_number=set_number,
                defaults={"weight": 0, "reps": 0},
            )

            form = SetLogForm(request.POST, instance=set_log)
            if form.is_valid():
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "weight": str(set_log.weight),
                        "reps": set_log.reps,
                    }
                )
            else:
                return JsonResponse({"success": False, "errors": form.errors})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class CompleteWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)

        if session.status != "active":
            messages.error(request, "Esta sessão não está ativa.")
            return redirect("logbook:routine_list")

        try:
            with transaction.atomic():

                session_form = WorkoutSessionForm(request.POST, instance=session)
                if session_form.is_valid():
                    session_form.save()

                session.status = "completed"
                session.end_time = timezone.now()
                session.save()

                messages.success(
                    request, f'Treino "{session.routine.name}" concluído com sucesso!'
                )
                return redirect("logbook:dashboard")
        except Exception as e:
            messages.error(request, f"Erro ao concluir treino: {str(e)}")
            return redirect("logbook:workout_session", pk=session_id)


class CancelWorkoutView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)

        if session.status != "active":
            messages.error(request, "Esta sessão não está ativa.")
            return redirect("logbook:routine_list")

        try:
            with transaction.atomic():
                routine_name = session.routine.name

                session.delete()

                messages.warning(
                    request, f'Treino "{routine_name}" cancelado e removido.'
                )
                return redirect("logbook:routine_list")
        except Exception as e:
            messages.error(request, f"Erro ao cancelar treino: {str(e)}")
            return redirect("logbook:workout_session", pk=session_id)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "logbook/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["stats"] = {
            "total_routines": Routine.objects.filter(user=self.request.user).count(),
            "total_exercises": Exercise.objects.filter(user=self.request.user).count(),
            "total_workouts": WorkoutSession.objects.filter(
                user=self.request.user, status="completed"
            ).count(),
            "workouts_this_week": WorkoutSession.objects.filter(
                user=self.request.user,
                status="completed",
                date__gte=timezone.now().date() - timedelta(days=7),
            ).count(),
        }

        context["recent_sessions"] = WorkoutSession.objects.filter(
            user=self.request.user, status="completed"
        ).order_by("-date", "-start_time")[:5]

        context["active_session"] = WorkoutSession.objects.filter(
            user=self.request.user, status="active"
        ).first()

        return context


class ExerciseProgressView(LoginRequiredMixin, TemplateView):
    template_name = "logbook/exercise_progress.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        user_exercises = Exercise.objects.filter(user=user).order_by("name")

        exercise_id = self.request.GET.get("exercise")
        period = self.request.GET.get("period", "90")

        selected_exercise = None
        stats = None
        chart_data = None
        recent_sets = None

        if exercise_id:
            try:
                selected_exercise = Exercise.objects.get(id=exercise_id, user=user)

                days_ago = int(period)
                start_date = date.today() - timedelta(days=days_ago)

                set_logs = SetLog.objects.filter(
                    exercise=selected_exercise,
                    workout_session__user=user,
                    workout_session__status="completed",
                    workout_session__date__gte=start_date,
                ).order_by("workout_session__date", "set_number")

                if set_logs.exists():

                    stats = {
                        "total_workouts": set_logs.values("workout_session")
                        .distinct()
                        .count(),
                        "total_sets": set_logs.count(),
                        "max_weight": set_logs.aggregate(models.Max("weight"))[
                            "weight__max"
                        ]
                        or 0,
                    }

                    chart_data = self._prepare_chart_data(set_logs)

                else:
                    stats = {
                        "total_workouts": 0,
                        "total_sets": 0,
                        "max_weight": 0,
                    }

            except (Exercise.DoesNotExist, ValueError):
                pass

        context.update(
            {
                "user_exercises": user_exercises,
                "selected_exercise": selected_exercise,
                "period": period,
                "stats": stats,
                "chart_data": chart_data,
            }
        )

        return context

    def _prepare_chart_data(self, set_logs):

        workout_data = {}
        session_weights = []

        for log in set_logs:
            workout_date = log.workout_session.date

            if workout_date not in workout_data:
                workout_data[workout_date] = {
                    "max_weight": float(log.weight),
                }
            else:
                workout_data[workout_date]["max_weight"] = max(
                    workout_data[workout_date]["max_weight"], float(log.weight)
                )

            session_weights.append({"date": workout_date, "weight": float(log.weight)})

        sorted_dates = sorted(workout_data.keys())

        max_labels = [date.strftime("%d/%m") for date in sorted_dates]
        max_weights = [workout_data[date]["max_weight"] for date in sorted_dates]

        session_labels = []
        session_weight_values = []

        for item in session_weights:
            session_labels.append(item["date"].strftime("%d/%m"))
            session_weight_values.append(item["weight"])

        chart_data = {
            "labels": max_labels,
            "datasets": [
                {
                    "label": "Peso Máximo",
                    "data": max_weights,
                    "borderColor": "#dc3545",
                    "backgroundColor": "rgba(220, 53, 69, 0.1)",
                    "tension": 0.3,
                    "fill": False,
                    "pointRadius": 5,
                    "pointHoverRadius": 8,
                },
                {
                    "label": "Peso de Sessão",
                    "data": session_weight_values,
                    "borderColor": "#28a745",
                    "backgroundColor": "rgba(40, 167, 69, 0.1)",
                    "tension": 0.1,
                    "fill": False,
                    "pointRadius": 3,
                    "pointHoverRadius": 5,
                    "showLine": True,
                },
            ],
            "session_labels": session_labels,
        }

        return json.dumps(chart_data)
