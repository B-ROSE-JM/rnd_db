from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Formulation, FormulationIngredient
from materials.models import Material


def _normalize_short_date(raw_value):
    value = (raw_value or '').strip()
    if not value:
        return ''

    digits = ''.join(ch for ch in value if ch.isdigit())
    if len(digits) != 6:
        raise ValueError('Manufacture date must be entered as YYMMDD or YY-MM-DD.')
    return f'{digits[:2]}-{digits[2:4]}-{digits[4:6]}'

def formulation_list(request):
    formulations = Formulation.objects.prefetch_related('ingredients__material').all().order_by('-created_at')
    
    # Extract unique condition keys
    condition_keys = set()
    for form in formulations:
        if isinstance(form.conditions, dict):
            condition_keys.update(form.conditions.keys())
    
    condition_keys = sorted(list(condition_keys))
    
    return render(request, 'formulations/list.html', {
        'formulations': formulations,
        'condition_keys': condition_keys
    })

def formulation_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        try:
            manufacture_date = _normalize_short_date(request.POST.get('manufacture_date'))
        except ValueError as exc:
            messages.error(request, str(exc))
            manufacture_date = request.POST.get('manufacture_date', '')
            materials = Material.objects.all()
            all_cond_keys = set()
            for form in Formulation.objects.all():
                if isinstance(form.conditions, dict):
                    all_cond_keys.update(form.conditions.keys())
            cond_fields = []
            for k in sorted(list(all_cond_keys)):
                cond_fields.append({'key': k, 'val': '', 'type': 'number'})
            return render(request, 'formulations/form.html', {
                'materials': materials,
                'cond_fields': cond_fields,
                'manufacture_date': manufacture_date,
                'form_data': request.POST,
            })
        description = request.POST.get('description', '')
        
        # Handle dynamic conditions
        conditions_dict = {}
        cond_keys = request.POST.getlist('condition_keys[]')
        cond_values = request.POST.getlist('condition_values[]')
        for k, v in zip(cond_keys, cond_values):
            k_st = k.strip()
            v_st = v.strip()
            if k_st and v_st:
                try:
                    f_val = float(v_st)
                    conditions_dict[k_st] = int(f_val) if f_val.is_integer() else f_val
                except ValueError:
                    conditions_dict[k_st] = v_st
                
        memo = request.POST.get('memo', '')
        formulation = Formulation.objects.create(
            name=name,
            manufacture_date=manufacture_date,
            description=description,
            conditions=conditions_dict,
            memo=memo
        )
        
        # Handle hierarchical ingredients list
        material_ids = request.POST.getlist('materials[]')
        ratios = request.POST.getlist('ratios[]')
        units = request.POST.getlist('units[]')
        
        for mat_id, ratio, unit in zip(material_ids, ratios, units):
            if mat_id and ratio:
                FormulationIngredient.objects.create(
                    formulation=formulation,
                    material_id=mat_id,
                    ratio_or_amount=float(ratio),
                    unit=unit
                )
                
        messages.success(request, 'Formulation successfully created.')
        return redirect('formulations:list')
        
    materials = Material.objects.all()
    
    # Get previously used condition keys for pre-population
    all_cond_keys = set()
    for form in Formulation.objects.all():
        if isinstance(form.conditions, dict):
            all_cond_keys.update(form.conditions.keys())
            
    cond_fields = []
    for k in sorted(list(all_cond_keys)):
        cond_fields.append({'key': k, 'val': '', 'type': 'number'})
    
    return render(request, 'formulations/form.html', {
        'materials': materials,
        'cond_fields': cond_fields,
        'manufacture_date': '',
    })

def formulation_edit(request, pk):
    formulation = get_object_or_404(Formulation, pk=pk)

    if request.method == 'POST':
        formulation.name = request.POST.get('name')
        try:
            formulation.manufacture_date = _normalize_short_date(request.POST.get('manufacture_date'))
        except ValueError as exc:
            messages.error(request, str(exc))
            materials = Material.objects.all()
            ingredients_data = []
            for ing in formulation.ingredients.all():
                options_html = '<option value="">Select a material...</option>'
                for mat in materials:
                    selected = ' selected' if ing.material_id == mat.id else ''
                    options_html += '<option value="{}"{}>{} ({})</option>'.format(
                        mat.id, selected, mat.name, mat.material_type
                    )
                ingredients_data.append({
                    'options_html': options_html,
                    'ratio': ing.ratio_or_amount,
                    'unit': ing.unit,
                })
            all_cond_keys = set()
            for form in Formulation.objects.all():
                if isinstance(form.conditions, dict):
                    all_cond_keys.update(form.conditions.keys())
            cond_fields = []
            for k in sorted(list(all_cond_keys)):
                val = formulation.conditions.get(k, '') if isinstance(formulation.conditions, dict) else ''
                val_type = 'number' if isinstance(val, (int, float)) else 'text'
                cond_fields.append({'key': k, 'val': val, 'type': val_type})
            return render(request, 'formulations/form.html', {
                'formulation': formulation,
                'materials': materials,
                'cond_fields': cond_fields,
                'ingredients_data': ingredients_data,
            })
        formulation.description = request.POST.get('description', '')
        
        # Handle dynamic conditions
        conditions_dict = {}
        cond_keys = request.POST.getlist('condition_keys[]')
        cond_values = request.POST.getlist('condition_values[]')
        for k, v in zip(cond_keys, cond_values):
            k_st = k.strip()
            v_st = v.strip()
            if k_st and v_st:
                try:
                    f_val = float(v_st)
                    conditions_dict[k_st] = int(f_val) if f_val.is_integer() else f_val
                except ValueError:
                    conditions_dict[k_st] = v_st
        formulation.conditions = conditions_dict
        formulation.memo = request.POST.get('memo', '')
        
        formulation.save()
        
        # Recreate hierarchical ingredients list
        formulation.ingredients.all().delete()
        
        material_ids = request.POST.getlist('materials[]')
        ratios = request.POST.getlist('ratios[]')
        units = request.POST.getlist('units[]')
        
        for mat_id, ratio, unit in zip(material_ids, ratios, units):
            if mat_id and ratio:
                FormulationIngredient.objects.create(
                    formulation=formulation,
                    material_id=mat_id,
                    ratio_or_amount=float(ratio),
                    unit=unit
                )
                
        messages.success(request, 'Formulation successfully updated.')
        return redirect('formulations:list')
        
    materials = Material.objects.all()
    
    # Build ingredients data with pre-rendered option HTML
    # to avoid using == in template (VSCode formatter strips spaces)
    ingredients_data = []
    for ing in formulation.ingredients.all():
        options_html = '<option value="">Select a material...</option>'
        for mat in materials:
            selected = ' selected' if ing.material_id == mat.id else ''
            options_html += '<option value="{}"{}>{} ({})</option>'.format(
                mat.id, selected, mat.name, mat.material_type
            )
        ingredients_data.append({
            'options_html': options_html,
            'ratio': ing.ratio_or_amount,
            'unit': ing.unit,
        })
    
    # Get previously used condition keys for pre-population
    all_cond_keys = set()
    for form in Formulation.objects.all():
        if isinstance(form.conditions, dict):
            all_cond_keys.update(form.conditions.keys())
            
    cond_fields = []
    for k in sorted(list(all_cond_keys)):
        val = formulation.conditions.get(k, '') if isinstance(formulation.conditions, dict) else ''
        val_type = 'number' if isinstance(val, (int, float)) else 'text'
        cond_fields.append({'key': k, 'val': val, 'type': val_type})
    
    return render(request, 'formulations/form.html', {
        'formulation': formulation,
        'materials': materials,
        'cond_fields': cond_fields,
        'ingredients_data': ingredients_data
    })
