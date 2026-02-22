from django.db import models
from materials.models import Material
import jsonfield

class Formulation(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    conditions = jsonfield.JSONField(default=dict, blank=True, help_text="Store custom mixing conditions, temperatures, etc.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class FormulationIngredient(models.Model):
    formulation = models.ForeignKey(Formulation, related_name='ingredients', on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    ratio_or_amount = models.FloatField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.material.name} - {self.ratio_or_amount} {self.unit}"
