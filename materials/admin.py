from django.contrib import admin
from .models import Material, SearchSlotConfig

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'material_type', 'created_at')
    search_fields = ('name', 'material_type')

@admin.register(SearchSlotConfig)
class SearchSlotConfigAdmin(admin.ModelAdmin):
    list_display = ('category', 'slot_1_name', 'slot_2_name', 'slot_3_name')
