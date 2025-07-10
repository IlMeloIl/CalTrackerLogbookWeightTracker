from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Food, DailyLog
from .forms import FoodForm, DailyLogForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from datetime import date
from django.http import JsonResponse

from django.db import transaction, models


class FoodListView(LoginRequiredMixin, ListView):
    model = Food
    template_name = "calories/food_list.html"
    context_object_name = "foods"

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)


class FoodCreateView(LoginRequiredMixin, CreateView):
    model = Food
    form_class = FoodForm
    template_name = "calories/food_form.html"
    success_url = reverse_lazy("calories:food_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class FoodUpdateView(LoginRequiredMixin, UpdateView):
    model = Food
    form_class = FoodForm
    template_name = "calories/food_form.html"
    success_url = reverse_lazy("calories:food_list")

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)


class FoodDeleteView(LoginRequiredMixin, DeleteView):
    model = Food
    template_name = "calories/food_confirm_delete.html"
    success_url = reverse_lazy("calories:food_list")

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)


class DailyLogView(LoginRequiredMixin, View):
    template_name = "calories/daily_log.html"

    def get(self, request, *args, **kwargs):
        today = date.today()
        daily_logs = DailyLog.objects.filter(user=request.user, date=today)

        total_calories = sum(log.calculated_calories for log in daily_logs)
        total_protein = sum(log.calculated_protein for log in daily_logs)
        total_carbs = sum(log.calculated_carbs for log in daily_logs)
        total_fat = sum(log.calculated_fat for log in daily_logs)

        user_foods = Food.objects.filter(user=request.user).order_by("name")

        context = {
            "date": today,
            "daily_logs": daily_logs,
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "user_foods": user_foods,
        }
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

        today = date.today()
        daily_logs = DailyLog.objects.filter(user=request.user, date=today)
        total_calories = sum(log.calculated_calories for log in daily_logs)
        total_protein = sum(log.calculated_protein for log in daily_logs)
        total_carbs = sum(log.calculated_carbs for log in daily_logs)
        total_fat = sum(log.calculated_fat for log in daily_logs)

        context = {
            "date": today,
            "daily_logs": daily_logs,
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "form": form,
        }
        return render(request, self.template_name, context)


class DailyLogDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyLog
    template_name = "calories/daily_log_confirm_delete.html"
    success_url = reverse_lazy("calories:daily_log")

    def get_queryset(self):
        return DailyLog.objects.filter(user=self.request.user)


class DailyLogEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        daily_log = get_object_or_404(DailyLog, pk=pk, user=request.user)
        quantity_grams = request.POST.get("quantity_grams")

        if quantity_grams:
            try:
                daily_log.quantity_grams = float(quantity_grams)
                daily_log.save()
                return JsonResponse({"success": True})
            except ValueError:
                return JsonResponse({"success": False, "error": "Quantidade inválida"})

        return JsonResponse({"success": False, "error": "Quantidade não fornecida"})


class FoodCreateAjaxView(LoginRequiredMixin, View):
    def post(self, request):
        form = FoodForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})


class FoodUpdateAjaxView(LoginRequiredMixin, View):
    def post(self, request, pk):
        food = get_object_or_404(Food, pk=pk, user=request.user)
        form = FoodForm(request.POST, instance=food)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "errors": form.errors})


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
