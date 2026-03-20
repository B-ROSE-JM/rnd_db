from django.shortcuts import render
from collections import Counter

def dashboard_view(request):
    try:
        from materials.models import Material
        from formulations.models import Formulation
        from experiments.models import Experiment

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
            'chart_labels': list(type_counts.keys()),
            'chart_data': list(type_counts.values()),
        }
    except Exception:
        # DB tables may not exist yet (fresh clone before migrate)
        context = {
            'materials_count': 0,
            'formulations_count': 0,
            'experiments_count': 0,
            'chart_labels': [],
            'chart_data': [],
        }
    return render(request, 'dashboard.html', context)
