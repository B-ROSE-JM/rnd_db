from django.shortcuts import render
from materials.models import Material
from formulations.models import Formulation
from experiments.models import Experiment
from collections import Counter

def dashboard_view(request):
    materials_count = Material.objects.count()
    formulations_count = Formulation.objects.count()
    experiments = Experiment.objects.all()
    experiments_count = experiments.count()
    
    # Calculate statistics for charts
    test_types_data = list(experiments.values_list('test_type', flat=True))
    type_counts = dict(Counter(test_types_data))
    
    context = {
        'materials_count': materials_count,
        'formulations_count': formulations_count,
        'experiments_count': experiments_count,
        
        # Chart data
        'chart_labels': list(type_counts.keys()),
        'chart_data': list(type_counts.values()),
    }
    return render(request, 'dashboard.html', context)
