from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Max, Min
from datetime import date, timedelta

User = get_user_model()


class WeightEntry(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weight_entries"
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Peso em kg"
    )
    date = models.DateField(help_text="Data da pesagem")

    class Meta:
        ordering = ["-date"]
        unique_together = ["user", "date"]

    def __str__(self):
        return f"{self.user.username} - {self.weight_kg}kg em {self.date}"

    @classmethod
    def get_user_metrics(cls, user):
        entries = cls.objects.filter(user=user)

        if not entries.exists():
            return {
                "current_weight": None,
                "max_weight": None,
                "min_weight": None,
                "entries_count": 0,
            }

        latest_entry = entries.first()
        current_weight = latest_entry.weight_kg

        aggregates = entries.aggregate(
            max_weight=Max("weight_kg"), min_weight=Min("weight_kg")
        )

        return {
            "current_weight": round(float(current_weight), 1),
            "max_weight": round(float(aggregates["max_weight"]), 1),
            "min_weight": round(float(aggregates["min_weight"]), 1),
            "entries_count": entries.count(),
        }

    @classmethod
    def get_chart_data(cls, user, days_limit=30):
        start_date = date.today() - timedelta(days=days_limit)
        entries = cls.objects.filter(user=user, date__gte=start_date).order_by("date")

        if not entries.exists():
            return {
                "labels": [],
                "data": [],
                "dates": [],
                "moving_average": [],
                "weekly_rate": None,
            }

        # Dados básicos
        labels = [entry.date.strftime("%d/%m") for entry in entries]
        data = [float(entry.weight_kg) for entry in entries]
        dates = [entry.date.strftime("%Y-%m-%d") for entry in entries]

        # Calcular moving average (média móvel de 7 dias)
        moving_average = []
        for i, entry in enumerate(entries):
            if i < 6:  # Primeiros 6 pontos não têm média móvel completa
                moving_average.append(None)
            else:
                # Média dos últimos 7 pontos
                recent_weights = [
                    float(entries[j].weight_kg) for j in range(i - 6, i + 1)
                ]
                avg = sum(recent_weights) / len(recent_weights)
                moving_average.append(round(avg, 2))

        # Calcular weekly rate (taxa semanal de mudança)
        weekly_rate = None
        if len(entries) >= 14:  # Precisa de pelo menos 2 semanas de dados
            # Converter para lista para permitir indexação negativa
            entries_list = list(entries)

            # Comparar média da primeira semana com média da última semana
            first_week = entries_list[:7]
            last_week = entries_list[-7:]

            first_week_avg = sum(float(e.weight_kg) for e in first_week) / len(
                first_week
            )
            last_week_avg = sum(float(e.weight_kg) for e in last_week) / len(last_week)

            weeks_diff = (entries_list[-1].date - entries_list[0].date).days / 7
            if weeks_diff > 0:
                weekly_rate = round((last_week_avg - first_week_avg) / weeks_diff, 2)

        chart_data = {
            "labels": labels,
            "data": data,
            "dates": dates,
            "moving_average": moving_average,
            "weekly_rate": weekly_rate,
            "count": entries.count(),
        }

        return chart_data
