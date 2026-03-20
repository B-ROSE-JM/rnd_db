from django.db import models
from materials.models import Material
import jsonfield

class Formulation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    conditions = jsonfield.JSONField(default=dict, blank=True, help_text="Mixing conditions like RPM, Temp, etc.")
    memo = models.TextField(blank=True, default='', help_text="Mixing instructions, SOP, or general notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
        
    @property
    def estimated_cost_per_kg(self):
        total_weight = sum(ing.ratio_or_amount for ing in self.ingredients.all())
        if total_weight == 0:
            return 0
        total_cost = sum(ing.ratio_or_amount * (ing.material.cost_per_kg or 0) for ing in self.ingredients.all())
        return round(total_cost / total_weight, 2)

class FormulationIngredient(models.Model):
    formulation = models.ForeignKey(Formulation, related_name='ingredients', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    ratio_or_amount = models.FloatField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.material.name} - {self.ratio_or_amount} {self.unit}"
