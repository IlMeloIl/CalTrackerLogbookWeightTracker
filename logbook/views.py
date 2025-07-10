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
from django.db import models, IntegrityError, transaction
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
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
                f"Não é possível excluir este exercício. Ele está sendo usado "
                f'nas rotinas: {", ".join(routine_names)}',
            )
            return redirect("logbook:exercise_list")

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
                        f'Exercício "{routine_exercise.exercise.name}" '
                        f"adicionado à rotina!",
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
                "Esta rotina não possui exercícios. Adicione exercícios "
                "antes de iniciar o treino.",
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
                "Esta rotina não possui exercícios. Adicione exercícios "
                "antes de iniciar o treino.",
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
                    f'Treino "{routine.name}" iniciado para '
                    f'{workout_date.strftime("%d/%m/%Y")}!',
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

        user_exercises = Exercise.objects.filter(
            Q(user=user) | Q(user__isnull=True)
        ).order_by("name")

        exercise_id = self.request.GET.get("exercise")
        period = self.request.GET.get("period", "90")

        selected_exercise = None
        stats = None
        chart_data = None
        recent_sets = None

        if exercise_id:
            try:
                selected_exercise = (
                    Exercise.objects.filter(id=exercise_id)
                    .filter(Q(user=user) | Q(user__isnull=True))
                    .first()
                )

                if not selected_exercise:
                    raise Exercise.DoesNotExist()

                days_ago = int(period)
                start_date = date.today() - timedelta(days=days_ago)

                set_logs = SetLog.objects.filter(
                    exercise=selected_exercise,
                    workout_session__user=user,
                    workout_session__status="completed",
                    workout_session__date__gte=start_date,
                ).order_by("workout_session__date", "set_number")

                if set_logs.exists():
                    total_workouts = (
                        set_logs.values("workout_session").distinct().count()
                    )
                    total_sets = set_logs.count()
                    max_weight = (
                        set_logs.aggregate(models.Max("weight"))["weight__max"] or 0
                    )

                    sets_per_workout = {}
                    for log in set_logs:
                        workout_id = log.workout_session.id
                        if workout_id not in sets_per_workout:
                            sets_per_workout[workout_id] = set()
                        sets_per_workout[workout_id].add(log.set_number)

                    avg_sets_per_workout = (
                        sum(len(sets) for sets in sets_per_workout.values())
                        / len(sets_per_workout)
                        if sets_per_workout
                        else 0
                    )
                    max_sets_in_workout = (
                        max(len(sets) for sets in sets_per_workout.values())
                        if sets_per_workout
                        else 0
                    )

                    avg_weight = (
                        set_logs.aggregate(models.Avg("weight"))["weight__avg"] or 0
                    )

                    stats = {
                        "total_workouts": total_workouts,
                        "total_sets": total_sets,
                        "max_weight": max_weight,
                        "avg_weight": round(avg_weight, 1),
                        "avg_sets_per_workout": round(avg_sets_per_workout, 1),
                        "max_sets_in_workout": max_sets_in_workout,
                    }

                    chart_data = self._prepare_chart_data(set_logs)

                    recent_sets = set_logs.order_by(
                        "-workout_session__date", "-set_number"
                    )[:10]

                else:
                    stats = {
                        "total_workouts": 0,
                        "total_sets": 0,
                        "max_weight": 0,
                        "avg_weight": 0,
                        "avg_sets_per_workout": 0,
                        "max_sets_in_workout": 0,
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
                "recent_sets": recent_sets,
            }
        )

        return context

    def _prepare_chart_data(self, set_logs):
        """
        Prepara dados do gráfico organizados por sets.
        Cada set terá sua própria série no gráfico.
        """
        workout_data = {}

        for log in set_logs:
            workout_date = log.workout_session.date
            set_number = log.set_number

            if workout_date not in workout_data:
                workout_data[workout_date] = {}

            if set_number not in workout_data[workout_date]:
                workout_data[workout_date][set_number] = []

            workout_data[workout_date][set_number].append(
                {
                    "weight": float(log.weight),
                    "reps": log.reps,
                    "datetime": log.workout_session.date,
                }
            )

        all_set_numbers = set()
        for date_data in workout_data.values():
            all_set_numbers.update(date_data.keys())

        all_set_numbers = sorted(all_set_numbers)

        datasets = []
        colors = [
            "#dc3545",  # Vermelho
            "#28a745",  # Verde
            "#007bff",  # Azul
            "#ffc107",  # Amarelo
            "#6f42c1",  # Roxo
            "#fd7e14",  # Laranja
            "#20c997",  # Teal
            "#e83e8c",  # Rosa
        ]

        sorted_dates = sorted(workout_data.keys())

        for i, set_num in enumerate(all_set_numbers):
            color = colors[i % len(colors)]

            set_data = []

            for workout_date in sorted_dates:
                if set_num in workout_data[workout_date]:
                    max_weight = max(
                        entry["weight"] for entry in workout_data[workout_date][set_num]
                    )
                    set_data.append(
                        {"x": workout_date.strftime("%Y-%m-%d"), "y": max_weight}
                    )
                else:
                    set_data.append({"x": workout_date.strftime("%Y-%m-%d"), "y": None})

            datasets.append(
                {
                    "label": f"Set {set_num}",
                    "data": set_data,
                    "borderColor": color,
                    "backgroundColor": color + "20",  # Adicionar transparência
                    "tension": 0.3,
                    "fill": False,
                    "pointRadius": 4,
                    "pointHoverRadius": 6,
                    "connectNulls": False,
                }
            )

        max_weight_data = []
        for workout_date in sorted_dates:
            max_weight = 0
            for set_data in workout_data[workout_date].values():
                for entry in set_data:
                    max_weight = max(max_weight, entry["weight"])

            max_weight_data.append(
                {"x": workout_date.strftime("%Y-%m-%d"), "y": max_weight}
            )

        datasets.append(
            {
                "label": "Peso Máximo do Treino",
                "data": max_weight_data,
                "borderColor": "#000000",
                "backgroundColor": "rgba(0, 0, 0, 0.1)",
                "tension": 0.3,
                "fill": False,
                "pointRadius": 6,
                "pointHoverRadius": 8,
                "borderWidth": 3,
                "borderDash": [5, 5],  # Linha tracejada
            }
        )

        chart_data = {
            "datasets": datasets,
            "dates": [date.strftime("%Y-%m-%d") for date in sorted_dates],
            "labels": [date.strftime("%d/%m") for date in sorted_dates],
        }

        return json.dumps(chart_data)


class RoutineDeleteAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        routine = get_object_or_404(Routine, pk=pk, user=request.user)

        active_sessions = WorkoutSession.objects.filter(
            routine=routine, status="active"
        )

        if active_sessions.exists():
            return JsonResponse(
                {
                    "success": False,
                    "error": "Não é possível excluir uma rotina com treinos ativos.",
                }
            )

        routine_name = routine.name
        routine.delete()
        return JsonResponse(
            {
                "success": True,
                "message": f'Rotina "{routine_name}" excluída com sucesso!',
            }
        )


class RoutineUpdateAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        routine = get_object_or_404(Routine, pk=pk, user=request.user)
        form = RoutineForm(request.POST, instance=routine, user=request.user)

        if form.is_valid():
            try:
                form.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": f'Rotina "{form.instance.name}" '
                        f"atualizada com sucesso!",
                    }
                )
            except IntegrityError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Você já tem uma rotina com este nome.",
                    }
                )
        else:
            return JsonResponse({"success": False, "errors": form.errors})


class ExerciseDeleteAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        exercise = get_object_or_404(Exercise, pk=pk, user=request.user)

        routine_uses = RoutineExercise.objects.filter(
            exercise=exercise, routine__user=request.user
        )

        if routine_uses.exists():
            routine_names = [ru.routine.name for ru in routine_uses[:3]]
            if len(routine_uses) > 3:
                routine_names.append("...")

            return JsonResponse(
                {
                    "success": False,
                    "error": f"Não é possível excluir este exercício. Ele está "
                    f'sendo usado nas rotinas: {", ".join(routine_names)}',
                }
            )

        exercise.delete()
        return JsonResponse({"success": True})


class ExerciseUpdateAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        exercise = get_object_or_404(Exercise, pk=pk, user=request.user)
        form = ExerciseForm(request.POST, instance=exercise, user=request.user)

        if form.is_valid():
            try:
                form.save()
                return JsonResponse({"success": True})
            except IntegrityError:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Você já tem um exercício com este nome.",
                    }
                )
        else:
            return JsonResponse({"success": False, "errors": form.errors})
