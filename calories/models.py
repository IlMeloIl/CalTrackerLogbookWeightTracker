from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()


class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="foods")
    name = models.CharField(max_length=100, help_text="Nome do alimento")
    serving_size_grams = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Tamanho da porção em gramas"
    )
    calories = models.IntegerField(help_text="Calorias por porção")
    protein = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Proteínas por porção (g)"
    )
    carbs = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Carboidratos por porção (g)"
    )
    fat = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Gorduras por porção (g)"
    )

    def __str__(self):
        return f"{self.name} ({self.serving_size_grams}g)"


class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_logs")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_grams = models.DecimalField(
        max_digits=7, decimal_places=2, help_text="Quantidade consumida em gramas"
    )
    date = models.DateField(auto_now_add=True, help_text="Data do registro")
    order = models.PositiveIntegerField(
        default=1, help_text="Ordem do alimento na lista do dia"
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.user.username} - {self.food.name} em {self.date}"

    @property
    def nutritional_factor(self):
        return (
            self.quantity_grams / self.food.serving_size_grams
            if self.food.serving_size_grams > 0
            else Decimal(0)
        )

    def _calcular_nutriente(self, valor_nutriente, usar_decimal=True):
        resultado = valor_nutriente * self.nutritional_factor
        return resultado.quantize(Decimal("0.01")) if usar_decimal else round(resultado)

    @property
    def calculated_calories(self):
        return self._calcular_nutriente(self.food.calories, usar_decimal=False)

    @property
    def calculated_protein(self):
        return self._calcular_nutriente(self.food.protein)

    @property
    def calculated_carbs(self):
        return self._calcular_nutriente(self.food.carbs)

    @property
    def calculated_fat(self):
        return self._calcular_nutriente(self.food.fat)
