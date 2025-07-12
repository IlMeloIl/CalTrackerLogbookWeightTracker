import json
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View

from .models import WeightEntry
from .forms import WeightEntryForm
from shared.utils import (
    AjaxFormProcessorMixin,
    AjaxCRUDMixin,
    ContextDataMixin,
)


class WeightTrackerView(ContextDataMixin, LoginRequiredMixin, View):
    template_name = "weight/weight_tracker.html"

    def _get_context_data(self, form=None):
        if form is None:
            form = WeightEntryForm(initial={"date": date.today()})

        all_entries = WeightEntry.objects.filter(user=self.request.user)
        paginator = Paginator(all_entries, 10)
        page_number = self.request.GET.get("page")
        entries = paginator.get_page(page_number)

        metrics = WeightEntry.get_user_metrics(self.request.user)

        dados_grafico = WeightEntry.get_chart_data(self.request.user, days_limit=365)

        return {
            "form": form,
            "entries": entries,
            "metrics": metrics,
            "chart_data": json.dumps(dados_grafico),
        }

    def _handle_unique_constraint_error(self, exception):
        if "unique constraint" in str(exception).lower():
            messages.error(
                self.request, "Já existe um registro de peso para esta data."
            )
        else:
            messages.error(self.request, "Erro ao salvar o registro. Tente novamente.")

    def get(self, request, *args, **kwargs):
        context = self._get_context_data()
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
                    f"Peso de {entry.weight_kg}kg registrado para "
                    f'{entry.date.strftime("%d/%m/%Y")}!',
                )
                return redirect("weight:tracker")
            except Exception as e:
                self._handle_unique_constraint_error(e)

        context = self._get_context_data(form)
        return render(request, self.template_name, context)


class ChartDataView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        days = int(request.GET.get("days", 365))
        chart_data = WeightEntry.get_chart_data(request.user, days_limit=days)
        return JsonResponse(chart_data)


class WeightEntryEditView(LoginRequiredMixin, View):
    def post(self, request, pk):

        dados_mapeados = request.POST.copy()
        if "peso_kg" in dados_mapeados:
            dados_mapeados["weight_kg"] = dados_mapeados["peso_kg"]
        if "data" in dados_mapeados:
            dados_mapeados["date"] = dados_mapeados["data"]

        return AjaxFormProcessorMixin.processar_edicao_ajax(
            WeightEntry, pk, request.user, dados_mapeados, ["weight_kg", "date"]
        )


class WeightEntryDeleteView(AjaxCRUDMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        return self.processar_delete_ajax(WeightEntry, pk)
