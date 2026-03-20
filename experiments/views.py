from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Experiment, ExperimentImage, ExperimentRawData
from formulations.models import Formulation
import csv

def experiment_list(request):
    query = request.GET.get('q', '').strip()
    
    experiments = Experiment.objects.select_related('formulation').prefetch_related('images', 'raw_files').all().order_by('-created_at')
    
    if query:
        experiments = experiments.filter(
            Q(formulation__name__icontains=query) |
            Q(test_type__icontains=query)
        ).distinct()
    
    # Extract unique result and condition keys
    result_keys = set()
    condition_keys = set()
    for exp in experiments:
        if isinstance(exp.results, dict):
            result_keys.update(exp.results.keys())
        if isinstance(exp.conditions, dict):
            condition_keys.update(exp.conditions.keys())
    
    result_keys = sorted(list(result_keys))
    condition_keys = sorted(list(condition_keys))
    
    return render(request, 'experiments/list.html', {
        'experiments': experiments,
        'result_keys': result_keys,
        'condition_keys': condition_keys
    })

def experiment_add(request):
    if request.method == 'POST':
        formulation_id = request.POST.get('formulation_id')
        test_type = request.POST.get('test_type')
        
        # Handle dynamic conditions
        conditions_dict = {}
        cond_keys = request.POST.getlist('condition_keys[]')
        cond_values = request.POST.getlist('condition_values[]')
        for k, v in zip(cond_keys, cond_values):
            k = k.strip()
            v = v.strip()
            if k and v:
                try:
                    conditions_dict[k] = float(v)
                except ValueError:
                    conditions_dict[k] = v

        # Handle dynamic result metrics
        results_dict = {}
        res_keys = request.POST.getlist('result_keys[]')
        res_values = request.POST.getlist('result_values[]')
        for k, v in zip(res_keys, res_values):
            k = k.strip()
            v = v.strip()
            if k and v:
                try:
                    results_dict[k] = float(v)
                except ValueError:
                    results_dict[k] = v
                
        memo = request.POST.get('memo', '')
        
        # Create base experiment record
        experiment = Experiment.objects.create(
            formulation_id=formulation_id,
            test_type=test_type,
            conditions=conditions_dict,
            results=results_dict,
            memo=memo
        )
        
        # Process multiple images
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            ExperimentImage.objects.create(experiment=experiment, image=img, description=desc)
            
        # Process multiple raw data files
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            ExperimentRawData.objects.create(experiment=experiment, file=r_file, description=desc)
            
        messages.success(request, 'Experiment data successfully logged.')
        return redirect('experiments:list')
        
    formulations = Formulation.objects.all()
    
    # Get previously used condition keys and result keys for pre-population
    all_cond_keys = set()
    all_res_keys = set()
    
    for exp in Experiment.objects.all():
        if isinstance(exp.conditions, dict):
            all_cond_keys.update(exp.conditions.keys())
        if isinstance(exp.results, dict):
            all_res_keys.update(exp.results.keys())
            
    cond_fields = []
    for k in sorted(list(all_cond_keys)):
        cond_fields.append({'key': k, 'val': '', 'type': 'text'})
        
    res_fields = []
    for k in sorted(list(all_res_keys)):
        res_fields.append({'key': k, 'val': '', 'type': 'text'})
    
    return render(request, 'experiments/form.html', {
        'formulations': formulations,
        'cond_fields': cond_fields,
        'res_fields': res_fields
    })


def experiment_compare(request):
    exp_ids = request.GET.getlist('exp_ids')
    if not exp_ids:
        messages.warning(request, "No experiments selected for comparison.")
        return redirect('experiments:list')
        
    experiments = Experiment.objects.filter(id__in=exp_ids).select_related('formulation').prefetch_related('images', 'raw_files')
    
    result_keys = set()
    condition_keys = set()
    chart_data = []
    
    for exp in experiments:
        if isinstance(exp.results, dict):
            result_keys.update(exp.results.keys())
        if isinstance(exp.conditions, dict):
            condition_keys.update(exp.conditions.keys())
            
        chart_data.append({
            'id': exp.id,
            'label': f"Exp #{exp.id} ({exp.formulation.name})",
            'conditions': exp.conditions if isinstance(exp.conditions, dict) else {},
            'results': exp.results if isinstance(exp.results, dict) else {},
        })
            
    import json
    return render(request, 'experiments/compare.html', {
        'experiments': experiments,
        'result_keys': sorted(list(result_keys)),
        'condition_keys': sorted(list(condition_keys)),
        'chart_data_json': json.dumps(chart_data)
    })

def experiment_delete(request, pk):
    exp = get_object_or_404(Experiment, pk=pk)
    exp.delete()
    messages.success(request, 'Experiment deleted successfully.')
    return redirect('experiments:list')

def experiment_edit(request, pk):
    experiment = get_object_or_404(Experiment, pk=pk)

    if request.method == 'POST':
        experiment.formulation_id = request.POST.get('formulation_id')
        experiment.test_type = request.POST.get('test_type')
        
        # Handle dynamic conditions
        conditions_dict = {}
        cond_keys = request.POST.getlist('condition_keys[]')
        cond_values = request.POST.getlist('condition_values[]')
        for k, v in zip(cond_keys, cond_values):
            k = k.strip()
            v = v.strip()
            if k and v:
                try:
                    conditions_dict[k] = float(v)
                except ValueError:
                    conditions_dict[k] = v
        experiment.conditions = conditions_dict

        # Handle dynamic result metrics
        results_dict = {}
        res_keys = request.POST.getlist('result_keys[]')
        res_values = request.POST.getlist('result_values[]')
        for k, v in zip(res_keys, res_values):
            k = k.strip()
            v = v.strip()
            if k and v:
                try:
                    results_dict[k] = float(v)
                except ValueError:
                    results_dict[k] = v
        experiment.results = results_dict
        experiment.memo = request.POST.get('memo', '')
                
        experiment.save()
        
        ExperimentImage.objects.filter(experiment=experiment).update(is_representative=False)
        rep_ids = request.POST.getlist('representative_image_ids[]')
        if rep_ids:
            ExperimentImage.objects.filter(id__in=rep_ids, experiment=experiment).update(is_representative=True)
        
        # Handle file deletions
        images_to_delete = request.POST.getlist('delete_image_ids[]')
        if images_to_delete:
            ExperimentImage.objects.filter(id__in=images_to_delete, experiment=experiment).delete()
            
        raw_to_delete = request.POST.getlist('delete_raw_ids[]')
        if raw_to_delete:
            ExperimentRawData.objects.filter(id__in=raw_to_delete, experiment=experiment).delete()
        
        # Process multiple images (new ones)
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            ExperimentImage.objects.create(experiment=experiment, image=img, description=desc)
            
        # Process multiple raw data files (new ones)
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            ExperimentRawData.objects.create(experiment=experiment, file=r_file, description=desc)
            
        messages.success(request, 'Experiment data successfully updated.')
        return redirect('experiments:list')
        
    formulations = Formulation.objects.all()
    
    # Get previously used condition keys and result keys for pre-population
    all_cond_keys = set()
    all_res_keys = set()
    
    for exp in Experiment.objects.all():
        if isinstance(exp.conditions, dict):
            all_cond_keys.update(exp.conditions.keys())
        if isinstance(exp.results, dict):
            all_res_keys.update(exp.results.keys())
            
    cond_fields = []
    for k in sorted(list(all_cond_keys)):
        val = experiment.conditions.get(k, '') if isinstance(experiment.conditions, dict) else ''
        input_type = 'number' if isinstance(val, (int, float)) and val != '' else 'text'
        cond_fields.append({'key': k, 'val': val, 'type': input_type})
        
    res_fields = []
    for k in sorted(list(all_res_keys)):
        val = experiment.results.get(k, '') if isinstance(experiment.results, dict) else ''
        input_type = 'number' if isinstance(val, (int, float)) and val != '' else 'text'
        res_fields.append({'key': k, 'val': val, 'type': input_type})
    
    # Pre-render existing files HTML to avoid VSCode formatter breaking template tags
    existing_images_html = ''
    for i, img in enumerate(experiment.images.all()):
        checked = 'checked' if img.is_representative else ''
        existing_images_html += (
            '<div style="display: flex; gap: 12px; align-items: center; padding: 8px; '
            'border: 1px solid var(--border-color); border-radius: 6px; background-color: white;">'
            '<img src="{}" style="height: 40px; border-radius: 4px;">'
            '<span style="flex: 1; font-size: 0.875rem; color: var(--text-main);">Image #{}</span>'
            '<label style="color: #047857; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer; margin-right: 12px;">'
            '<input type="checkbox" name="representative_image_ids[]" value="{}" {}> 대표 이미지 지정'
            '</label>'
            '<label style="color: #EF4444; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer;">'
            '<input type="checkbox" name="delete_image_ids[]" value="{}"> Delete'
            '</label></div>'
        ).format(img.image.url, i + 1, img.id, checked, img.id)
    
    existing_raw_html = ''
    for rf in experiment.raw_files.all():
        existing_raw_html += (
            '<div style="display: flex; gap: 12px; align-items: center; padding: 8px; '
            'border: 1px solid var(--border-color); border-radius: 6px; background-color: white;">'
            '<i class="fas fa-file-csv" style="color: #10B981; font-size: 1.5rem;"></i>'
            '<span style="flex: 1; font-size: 0.875rem; color: var(--text-main);">{}</span>'
            '<label style="color: #EF4444; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer;">'
            '<input type="checkbox" name="delete_raw_ids[]" value="{}"> Delete'
            '</label></div>'
        ).format(rf.file.name, rf.id)
    
    return render(request, 'experiments/form.html', {
        'experiment': experiment,
        'formulations': formulations,
        'cond_fields': cond_fields,
        'res_fields': res_fields,
        'existing_images_html': existing_images_html,
        'existing_raw_html': existing_raw_html
    })
