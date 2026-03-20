from django.db import models
import jsonfield
from django.core.validators import FileExtensionValidator
from rnd_platform.utils import (
    validate_file_size, get_mm_image_path, get_mm_raw_data_path, move_file_to_trash
)
from django.db.models.signals import post_delete
from django.dispatch import receiver

class MetalMaterial(models.Model):
    name = models.CharField(max_length=255)
    material_type = models.CharField(max_length=100)
    
    num_attr_1 = models.FloatField(null=True, blank=True)
    num_attr_2 = models.FloatField(null=True, blank=True)
    num_attr_3 = models.FloatField(null=True, blank=True)
    num_attr_4 = models.FloatField(null=True, blank=True)
    num_attr_5 = models.FloatField(null=True, blank=True)
    
    custom_attributes = jsonfield.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MMImage(models.Model):
    material = models.ForeignKey(MetalMaterial, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_mm_image_path, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])])
    description = models.CharField(max_length=255, blank=True, help_text="Optional caption or description for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.material.name}"

class MMRawData(models.Model):
    material = models.ForeignKey(MetalMaterial, on_delete=models.CASCADE, related_name='raw_files')
    file = models.FileField(upload_to=get_mm_raw_data_path, validators=[validate_file_size, FileExtensionValidator(allowed_extensions=['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'jpg', 'jpeg', 'png', 'txt'])])
    description = models.CharField(max_length=255, blank=True, help_text="Optional description for the uploaded file(s)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Raw Data for {self.material.name}"

@receiver(post_delete, sender=MMImage)
def trash_mm_image(sender, instance, **kwargs):
    move_file_to_trash(instance.image, 'mm', 'images')

@receiver(post_delete, sender=MMRawData)
def trash_mm_raw_data(sender, instance, **kwargs):
    move_file_to_trash(instance.file, 'mm', 'raw_data')
