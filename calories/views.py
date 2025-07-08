from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Food, DailyLog
from .forms import FoodForm, DailyLogForm
from django.shortcuts import render, redirect 
from django.views import View
from datetime import date


class FoodListView(LoginRequiredMixin, ListView):
    model = Food
    template_name = 'calories/food_list.html'
    context_object_name = 'foods'

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)

class FoodCreateView(LoginRequiredMixin, CreateView):
    model = Food
    form_class = FoodForm
    template_name = 'calories/food_form.html'
    success_url = reverse_lazy('calories:food_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class FoodUpdateView(LoginRequiredMixin, UpdateView):
    model = Food
    form_class = FoodForm
    template_name = 'calories/food_form.html'
    success_url = reverse_lazy('calories:food_list')

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)

class FoodDeleteView(LoginRequiredMixin, DeleteView):
    model = Food
    template_name = 'calories/food_confirm_delete.html'
    success_url = reverse_lazy('calories:food_list')

    def get_queryset(self):
        return Food.objects.filter(user=self.request.user)

class DailyLogView(LoginRequiredMixin, View):
    template_name = 'calories/daily_log.html'

    def get(self, request, *args, **kwargs):
        today = date.today()
        daily_logs = DailyLog.objects.filter(user=request.user, date=today)
                
        total_calories = sum(log.calculated_calories for log in daily_logs)
        total_protein = sum(log.calculated_protein for log in daily_logs)
        total_carbs = sum(log.calculated_carbs for log in daily_logs)
        total_fat = sum(log.calculated_fat for log in daily_logs)
        
        form = DailyLogForm(user=request.user)
        context = {
            'date': today,
            'daily_logs': daily_logs,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = DailyLogForm(request.POST, user=request.user)
        if form.is_valid():
            log_entry = form.save(commit=False)
            log_entry.user = request.user            
            log_entry.save()
            return redirect('calories:daily_log')
        
        today = date.today()
        daily_logs = DailyLog.objects.filter(user=request.user, date=today)
        total_calories = sum(log.calculated_calories for log in daily_logs)
        total_protein = sum(log.calculated_protein for log in daily_logs)
        total_carbs = sum(log.calculated_carbs for log in daily_logs)
        total_fat = sum(log.calculated_fat for log in daily_logs)
        
        context = {
            'date': today,
            'daily_logs': daily_logs,
            'total_calories': total_calories,
            'total_protein': total_protein,
            'total_carbs': total_carbs,
            'total_fat': total_fat,
            'form': form, 
        }
        return render(request, self.template_name, context)

class DailyLogDeleteView(LoginRequiredMixin, DeleteView):
    model = DailyLog
    template_name = 'calories/daily_log_confirm_delete.html'
    success_url = reverse_lazy('calories:daily_log')

    def get_queryset(self):
        return DailyLog.objects.filter(user=self.request.user)