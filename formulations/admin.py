from django.contrib import admin
from .models import Formulation, FormulationIngredient

class IngredientInline(admin.TabularInline):
    model = FormulationIngredient
    extra = 1

@admin.register(Formulation)
class FormulationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    inlines = [IngredientInline]
