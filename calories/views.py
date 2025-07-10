from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.db import transaction, models
from datetime import date

from .models import Food, DailyLog
from .forms import FoodForm, DailyLogForm


class BaseUserFilterMixin:
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class BaseFoodView(LoginRequiredMixin, BaseUserFilterMixin):
    model = Food
    form_class = FoodForm
    template_name = "calories/food_form.html"
    success_url = reverse_lazy("calories:daily_log")


class FoodCreateView(BaseFoodView, CreateView):
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FoodUpdateView(BaseFoodView, UpdateView):
    pass


class FoodDeleteView(LoginRequiredMixin, BaseUserFilterMixin, DeleteView):
    model = Food
    template_name = "calories/food_confirm_delete.html"
    success_url = reverse_lazy("calories:daily_log")

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


class DailyLogDeleteView(LoginRequiredMixin, BaseUserFilterMixin, DeleteView):
    model = DailyLog
    template_name = "calories/daily_log_confirm_delete.html"
    success_url = reverse_lazy("calories:daily_log")


class DailyLogEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        daily_log = get_object_or_404(DailyLog, pk=pk, user=request.user)
        quantity_grams = request.POST.get("quantity_grams")

        if not quantity_grams:
            return JsonResponse({"success": False, "error": "Quantidade não fornecida"})

        try:
            daily_log.quantity_grams = float(quantity_grams)
            daily_log.save()
            return JsonResponse({"success": True})
        except ValueError:
            return JsonResponse({"success": False, "error": "Quantidade inválida"})


class BaseFoodAjaxView(LoginRequiredMixin, View):
    def _processar_form(self, form):
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "errors": form.errors})


class FoodCreateAjaxView(BaseFoodAjaxView):
    def post(self, request):
        form = FoodForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
        return self._processar_form(form)


class FoodUpdateAjaxView(BaseFoodAjaxView):
    def post(self, request, pk):
        food = get_object_or_404(Food, pk=pk, user=request.user)
        form = FoodForm(request.POST, instance=food)
        return self._processar_form(form)


class ReorderDailyLogsView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            food_ids = request.POST.getlist("food_ids[]")
            today = date.today()

            with transaction.atomic():
                for i, food_id in enumerate(food_ids, 1):
                    DailyLog.objects.filter(
                        user=request.user, date=today, pk=food_id
                    ).update(order=i)

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
