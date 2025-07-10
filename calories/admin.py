from django.contrib import admin
from .models import Food, DailyLog


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "serving_size_grams", "calories"]
    list_filter = ["user"]
    search_fields = ["name"]


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ["user", "food", "quantity_grams", "date", "order"]
    list_filter = ["user", "date"]
    search_fields = ["food__name", "user__username"]
