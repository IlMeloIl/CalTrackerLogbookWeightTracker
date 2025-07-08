from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from datetime import date
from .models import WeightEntry
from .forms import WeightEntryForm
import json
from django.http import JsonResponse

class WeightTrackerView(LoginRequiredMixin, View):
    template_name = 'weight/weight_tracker.html'

    def get(self, request, *args, **kwargs):
        form = WeightEntryForm(initial={'date': date.today()})
        entries = WeightEntry.objects.filter(user=request.user)[:10]
        
        metrics = WeightEntry.get_user_metrics(request.user)
        chart_data = WeightEntry.get_chart_data(request.user, days_limit=365)
        
        context = {
            'form': form,
            'entries': entries,
            'metrics': metrics,
            'chart_data': json.dumps(chart_data),
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = WeightEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            try:
                entry.save()
                messages.success(
                    request, 
                    f'Peso de {entry.weight_kg}kg registrado para {entry.date.strftime("%d/%m/%Y")}!'
                )
                return redirect('weight:tracker')
            except Exception as e:
                if 'unique constraint' in str(e).lower():
                    messages.error(request, 'Já existe um registro de peso para esta data.')
                else:
                    messages.error(request, 'Erro ao salvar o registro. Tente novamente.')
        
        entries = WeightEntry.objects.filter(user=request.user)[:10]
        metrics = WeightEntry.get_user_metrics(request.user)
        chart_data = WeightEntry.get_chart_data(request.user, days_limit=365)
        
        context = {
            'form': form,
            'entries': entries,
            'metrics': metrics,
            'chart_data': json.dumps(chart_data),
        }
        return render(request, self.template_name, context)

class ChartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        days = int(request.GET.get('days', 365))
        chart_data = WeightEntry.get_chart_data(request.user, days_limit=days)
        return JsonResponse(chart_data)