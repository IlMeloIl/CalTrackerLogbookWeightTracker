from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()

class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foods')
    name = models.CharField(max_length=100, help_text="Nome do alimento")
    serving_size_grams = models.DecimalField(max_digits=7, decimal_places=2, help_text="Tamanho da porção em gramas")
    calories = models.IntegerField(help_text="Calorias por porção")
    protein = models.DecimalField(max_digits=5, decimal_places=2, help_text="Proteínas por porção (g)")
    carbs = models.DecimalField(max_digits=5, decimal_places=2, help_text="Carboidratos por porção (g)")
    fat = models.DecimalField(max_digits=5, decimal_places=2, help_text="Gorduras por porção (g)")

    def __str__(self):
        return f"{self.name} ({self.serving_size_grams}g)"

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_grams = models.DecimalField(max_digits=7, decimal_places=2, help_text="Quantidade consumida em gramas")
    date = models.DateField(auto_now_add=True, help_text="Data do registro")

    def __str__(self):
        return f"{self.user.username} - {self.food.name} em {self.date}"

    @property
    def nutritional_factor(self):
        if self.food.serving_size_grams > 0:
            return self.quantity_grams / self.food.serving_size_grams
        return Decimal(0)

    @property
    def calculated_calories(self):
        return round(self.food.calories * self.nutritional_factor)

    @property
    def calculated_protein(self):
        return (self.food.protein * self.nutritional_factor).quantize(Decimal('0.01'))

    @property
    def calculated_carbs(self):
        return (self.food.carbs * self.nutritional_factor).quantize(Decimal('0.01'))

    @property
    def calculated_fat(self):
        return (self.food.fat * self.nutritional_factor).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.user.username} - {self.food.name} em {self.date}"