from django.db import models
import jsonfield

class Material(models.Model):
    name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=100)
    custom_attributes = jsonfield.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # TEA (Techno-Economic Analysis) fields
    cost_per_kg = models.FloatField(null=True, blank=True, help_text="Estimated cost in USD per kg")
    is_commercial = models.BooleanField(default=False, help_text="Is this material commercially available?")

    def __str__(self):
        return self.name

class MaterialImage(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='materials/images/')
    description = models.CharField(max_length=255, blank=True, help_text="Optional caption or description for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.material.name}"

class MaterialRawData(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='raw_files')
    file = models.FileField(upload_to='materials/raw_data/')
    description = models.CharField(max_length=255, blank=True, help_text="Optional description for the uploaded file(s)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Raw Data for {self.material.name}"

class SearchSlotConfig(models.Model):
    CATEGORY_CHOICES = [
        ('mm', 'Metal Material'),
        ('om', 'Organic Material'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    slot_1_name = models.CharField(max_length=50, blank=True, help_text="Search Name for Slot 1 (e.g. Density)")
    slot_2_name = models.CharField(max_length=50, blank=True, help_text="Search Name for Slot 2")
    slot_3_name = models.CharField(max_length=50, blank=True, help_text="Search Name for Slot 3")
    slot_4_name = models.CharField(max_length=50, blank=True, help_text="Search Name for Slot 4")
    slot_5_name = models.CharField(max_length=50, blank=True, help_text="Search Name for Slot 5")

    def __str__(self):
        return f"{self.get_category_display()} Search Slots Configuration"
