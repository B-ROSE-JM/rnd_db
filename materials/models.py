from django.db import models
import jsonfield

class Material(models.Model):
    name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=100)
    custom_attributes = jsonfield.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
