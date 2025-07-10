from django.contrib import admin
from .models import WeightEntry


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "weight_kg", "date"]
    list_filter = ["user", "date"]
    search_fields = ["user__username"]
    date_hierarchy = "date"
    ordering = ["-date"]
