from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.db import models
from datetime import date

from .models import Food, DailyLog
from .forms import FoodForm, DailyLogForm
from shared.utils import (
    AjaxFormProcessorMixin,
    BaseUserCreateView,
    BaseUserUpdateView,
    BaseUserDeleteView,
    ReorderMixin,
    AjaxCRUDMixin,
)


class FoodCreateView(BaseUserCreateView):
    model = Food
    form_class = FoodForm
    template_name = "calories/food_form.html"
    success_url = reverse_lazy("calories:daily_log")

    def get_mensagem_sucesso_criacao(self):
        if hasattr(self, "object") and self.object and hasattr(self.object, "name"):
            return f'Alimento "{self.object.name}" criado com sucesso!'
        return f"Alimento criado com sucesso!"


class FoodUpdateView(BaseUserUpdateView):
    model = Food
    form_class = FoodForm
    template_name = "calories/food_form.html"
    success_url = reverse_lazy("calories:daily_log")

    def get_mensagem_sucesso_atualizacao(self):
        if hasattr(self, "object") and self.object and hasattr(self.object, "name"):
            return f'Alimento "{self.object.name}" atualizado com sucesso!'
        return f"Alimento atualizado com sucesso!"


class FoodDeleteView(BaseUserDeleteView):
    model = Food
    template_name = "calories/food_confirm_delete.html"
    success_url = reverse_lazy("calories:daily_log")

    def get_mensagem_sucesso_exclusao(self):
        return f"Alimento excluído com sucesso!"

    def get_success_url(self):
        next_url = self.request.POST.get("next")
        if next_url:
            return next_url
        return super().get_success_url()


class DailyLogUtils:
    @staticmethod
    def calcular_totais_nutricionais(daily_logs):
        return {
            "total_calories": sum(log.calculated_calories for log in daily_logs),
            "total_protein": sum(log.calculated_protein for log in daily_logs),
            "total_carbs": sum(log.calculated_carbs for log in daily_logs),
            "total_fat": sum(log.calculated_fat for log in daily_logs),
        }


class DailyLogView(LoginRequiredMixin, View):
    template_name = "calories/daily_log.html"

    def _get_daily_context(self, form=None):
        today = date.today()
        daily_logs = DailyLog.objects.filter(user=self.request.user, date=today)
        user_foods = Food.objects.filter(user=self.request.user).order_by("name")

        context = {
            "date": today,
            "daily_logs": daily_logs,
            "user_foods": user_foods,
        }
        context.update(DailyLogUtils.calcular_totais_nutricionais(daily_logs))

        if form:
            context["form"] = form
        return context

    def get(self, request, *args, **kwargs):
        context = self._get_daily_context()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = DailyLogForm(request.POST, user=request.user)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.user = request.user

            today = date.today()
            last_order = (
                DailyLog.objects.filter(user=request.user, date=today).aggregate(
                    models.Max("order")
                )["order__max"]
                or 0
            )
            log_entry.order = last_order + 1
            log_entry.save()
            return redirect("calories:daily_log")

        context = self._get_daily_context(form)
        return render(request, self.template_name, context)


class DailyLogDeleteView(BaseUserDeleteView):
    model = DailyLog
    template_name = "calories/daily_log_confirm_delete.html"
    success_url = reverse_lazy("calories:daily_log")

    def get_mensagem_sucesso_exclusao(self):
        return "Registro do diário excluído com sucesso!"


class DailyLogEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        return AjaxFormProcessorMixin.processar_edicao_ajax(
            DailyLog, pk, request.user, request.POST, ["quantity_grams"]
        )


class FoodCreateAjaxView(AjaxCRUDMixin, LoginRequiredMixin, View):
    def post(self, request):
        form = FoodForm(request.POST)
        return AjaxFormProcessorMixin.processar_formulario_ajax(
            form, usuario=request.user
        )


class FoodUpdateAjaxView(AjaxCRUDMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        return self.processar_update_ajax(Food, pk, FoodForm)


class ReorderDailyLogsView(ReorderMixin, LoginRequiredMixin, View):
    def post(self, request):
        food_ids = request.POST.getlist("food_ids[]")
        today = date.today()

        return self.processar_reordenacao(
            DailyLog, food_ids, campo_filtro="user", filtros_extras={"date": today}
        )
