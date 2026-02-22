from django.contrib import admin
from .models import Experiment

@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('formulation', 'test_type', 'created_at')
    search_fields = ('test_type',)
