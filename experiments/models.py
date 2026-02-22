from django.db import models
from formulations.models import Formulation
import jsonfield

class Experiment(models.Model):
    formulation = models.ForeignKey(Formulation, on_delete=models.CASCADE, related_name='experiments', help_text="The mixture/formulation tested.")
    test_type = models.CharField(max_length=100, help_text="e.g. Tensile Strength Test, Density Measurement")
    
    conditions = jsonfield.JSONField(default=dict, blank=True, help_text="Dynamic conditions specific to the experiment (e.g. Temperature, Operator)")
    results = jsonfield.JSONField(default=dict, blank=True, help_text="Dynamic key-value pairs for test results. e.g. {'Yield Strength': '45 MPa'}")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.formulation.name} - {self.test_type}"


class ExperimentImage(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='experiments/images/')
    description = models.CharField(max_length=255, blank=True, help_text="Optional caption or description for the image")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.experiment.id}"


class ExperimentRawData(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='raw_files')
    file = models.FileField(upload_to='experiments/raw_data/')
    description = models.CharField(max_length=255, blank=True, help_text="Optional description for the uploaded file(s)")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Raw Data for {self.experiment.id}"
