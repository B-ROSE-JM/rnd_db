from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import json
from django.http import JsonResponse
from .models import MetalMaterial, MMImage, MMRawData
from materials.models import SearchSlotConfig

def mm_list(request):
    mm = MetalMaterial.objects.prefetch_related('images', 'raw_files').all().order_by('-created_at')
    
    custom_keys = set()
    for mat in mm:
        if isinstance(mat.custom_attributes, dict):
            custom_keys.update(mat.custom_attributes.keys())
            
    config = SearchSlotConfig.objects.filter(category='mm').first()
    
    custom_keys = sorted(list(custom_keys))
    
    return render(request, 'mm/list.html', {
        'mm': mm,
        'custom_keys': custom_keys,
        'slot_config': config
    })

def _parse_slots(config, keys, values):
    slot_names = {}
    if config:
        if config.slot_1_name: slot_names[config.slot_1_name.strip().title()] = 'num_attr_1'
        if config.slot_2_name: slot_names[config.slot_2_name.strip().title()] = 'num_attr_2'
        if config.slot_3_name: slot_names[config.slot_3_name.strip().title()] = 'num_attr_3'
        if config.slot_4_name: slot_names[config.slot_4_name.strip().title()] = 'num_attr_4'
        if config.slot_5_name: slot_names[config.slot_5_name.strip().title()] = 'num_attr_5'

    custom_attrs = {}
    slot_values = {'num_attr_1': None, 'num_attr_2': None, 'num_attr_3': None, 'num_attr_4': None, 'num_attr_5': None}
    
    for k, v in zip(keys, values):
        val_str = str(v).strip()
        if k and k.strip() and val_str:
            normalized_key = k.strip().title()
            slot_field = slot_names.get(normalized_key)
            if slot_field:
                try:
                    slot_values[slot_field] = float(val_str)
                except (ValueError, TypeError):
                    custom_attrs[normalized_key] = val_str
            else:
                custom_attrs[normalized_key] = val_str
    
    return custom_attrs, slot_values

def mm_add(request):
    config = SearchSlotConfig.objects.filter(category='mm').first()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        material_type = request.POST.get('material_type')
        
        keys = request.POST.getlist('custom_keys[]')
        values = request.POST.getlist('custom_values[]')
        
        custom_attrs, slot_values = _parse_slots(config, keys, values)
        
        cost_per_kg = request.POST.get('cost_per_kg')
        is_commercial = request.POST.get('is_commercial') == 'on'
                
        mm = MetalMaterial.objects.create(
            name=name,
            material_type=material_type,
            cost_per_kg=float(cost_per_kg) if cost_per_kg else None,
            is_commercial=is_commercial,
            custom_attributes=custom_attrs,
            num_attr_1=slot_values['num_attr_1'],
            num_attr_2=slot_values['num_attr_2'],
            num_attr_3=slot_values['num_attr_3'],
            num_attr_4=slot_values['num_attr_4'],
            num_attr_5=slot_values['num_attr_5']
        )
        
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            MMImage.objects.create(mm=mm, image=img, description=desc)
            
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            MMRawData.objects.create(mm=mm, file=r_file, description=desc)
        
        messages.success(request, 'MetalMaterial successfully created with custom attributes and files.')
        return redirect('mm:list')
        
    all_keys = set()
    for mat in MetalMaterial.objects.all():
        if isinstance(mat.custom_attributes, dict):
            all_keys.update(mat.custom_attributes.keys())
            
    if config:
        for s_name in [config.slot_1_name, config.slot_2_name, config.slot_3_name, config.slot_4_name, config.slot_5_name]:
            if s_name: all_keys.add(s_name.strip().title())
            
    custom_fields = []
    for k in sorted(list(all_keys)):
        custom_fields.append({'key': k, 'val': ''})
    
    existing_types = list(MetalMaterial.objects.values_list('material_type', flat=True).distinct().order_by('material_type'))
    
    return render(request, 'mm/form.html', {
        'custom_fields': custom_fields,
        'existing_types': existing_types
    })

def mm_edit(request, pk):
    mm = get_object_or_404(MetalMaterial, pk=pk)
    config = SearchSlotConfig.objects.filter(category='mm').first()

    if request.method == 'POST':
        mm.name = request.POST.get('name')
        mm.material_type = request.POST.get('material_type')
        
        keys = request.POST.getlist('custom_keys[]')
        values = request.POST.getlist('custom_values[]')
        
        custom_attrs, slot_values = _parse_slots(config, keys, values)
        mm.custom_attributes = custom_attrs
        
        cost_per_kg = request.POST.get('cost_per_kg')
        mm.cost_per_kg = float(cost_per_kg) if cost_per_kg else None
        mm.is_commercial = request.POST.get('is_commercial') == 'on'
        
        mm.num_attr_1 = slot_values['num_attr_1']
        mm.num_attr_2 = slot_values['num_attr_2']
        mm.num_attr_3 = slot_values['num_attr_3']
        mm.num_attr_4 = slot_values['num_attr_4']
        mm.num_attr_5 = slot_values['num_attr_5']
        
        mm.save()
        
        images_to_delete = request.POST.getlist('delete_image_ids[]')
        if images_to_delete:
            MMImage.objects.filter(id__in=images_to_delete, mm=mm).delete()
            
        raw_to_delete = request.POST.getlist('delete_raw_ids[]')
        if raw_to_delete:
            MMRawData.objects.filter(id__in=raw_to_delete, mm=mm).delete()
            
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            MMImage.objects.create(mm=mm, image=img, description=desc)
            
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            MMRawData.objects.create(mm=mm, file=r_file, description=desc)
        
        messages.success(request, 'MetalMaterial successfully updated.')
        return redirect('mm:list')
        
    all_keys = set()
    for mat in MetalMaterial.objects.all():
        if isinstance(mat.custom_attributes, dict):
            all_keys.update(mat.custom_attributes.keys())
            
    slot_mapping = {}
    if config:
        if config.slot_1_name: 
            norm_name = config.slot_1_name.strip().title()
            all_keys.add(norm_name)
            slot_mapping[norm_name] = mm.num_attr_1
        if config.slot_2_name: 
            norm_name = config.slot_2_name.strip().title()
            all_keys.add(norm_name)
            slot_mapping[norm_name] = mm.num_attr_2
        if config.slot_3_name: 
            norm_name = config.slot_3_name.strip().title()
            all_keys.add(norm_name)
            slot_mapping[norm_name] = mm.num_attr_3
        if config.slot_4_name: 
            norm_name = config.slot_4_name.strip().title()
            all_keys.add(norm_name)
            slot_mapping[norm_name] = mm.num_attr_4
        if config.slot_5_name: 
            norm_name = config.slot_5_name.strip().title()
            all_keys.add(norm_name)
            slot_mapping[norm_name] = mm.num_attr_5
            
    custom_fields = []
    for k in sorted(list(all_keys)):
        if k in slot_mapping and slot_mapping[k] is not None:
            val = slot_mapping[k]
        else:
            val = mm.custom_attributes.get(k, '') if isinstance(mm.custom_attributes, dict) else ''
        custom_fields.append({'key': k, 'val': val})
    
    existing_types = list(MetalMaterial.objects.values_list('material_type', flat=True).distinct().order_by('material_type'))
    
    existing_images_html = ''
    for i, img in enumerate(mm.images.all()):
        existing_images_html += (
            '<div style="display: flex; gap: 12px; align-items: center; padding: 8px; '
            'border: 1px solid var(--border-color); border-radius: 6px; background-color: white;">'
            '<img src="{}" style="height: 40px; border-radius: 4px;">'
            '<span style="flex: 1; font-size: 0.875rem; color: var(--text-main);">Image #{}</span>'
            '<label style="color: #EF4444; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer;">'
            '<input type="checkbox" name="delete_image_ids[]" value="{}"> Delete'
            '</label></div>'
        ).format(img.image.url, i + 1, img.id)
    
    existing_raw_html = ''
    for rf in mm.raw_files.all():
        existing_raw_html += (
            '<div style="display: flex; gap: 12px; align-items: center; padding: 8px; '
            'border: 1px solid var(--border-color); border-radius: 6px; background-color: white;">'
            '<i class="fas fa-file-csv" style="color: #10B981; font-size: 1.5rem;"></i>'
            '<span style="flex: 1; font-size: 0.875rem; color: var(--text-main);">{}</span>'
            '<label style="color: #EF4444; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer;">'
            '<input type="checkbox" name="delete_raw_ids[]" value="{}"> Delete'
            '</label></div>'
        ).format(rf.file.name, rf.id)
            
    return render(request, 'mm/form.html', {
        'mm': mm,
        'custom_fields': custom_fields,
        'existing_types': existing_types,
        'existing_images_html': existing_images_html,
        'existing_raw_html': existing_raw_html
    })

def mm_batch_import(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            materials_data = data.get('materials', [])
            config = SearchSlotConfig.objects.filter(category='mm').first()
            
            created_count = 0
            for item in materials_data:
                name = item.get('name')
                mtype = item.get('material_type', 'Uncategorized')
                raw_custom_attrs = item.get('custom_attributes', {})
                
                keys = list(raw_custom_attrs.keys())
                values = list(raw_custom_attrs.values())
                
                custom_attrs, slot_values = _parse_slots(config, keys, values)
                
                if name:
                    MetalMaterial.objects.create(
                        name=name,
                        material_type=mtype,
                        custom_attributes=custom_attrs,
                        num_attr_1=slot_values['num_attr_1'],
                        num_attr_2=slot_values['num_attr_2'],
                        num_attr_3=slot_values['num_attr_3'],
                        num_attr_4=slot_values['num_attr_4'],
                        num_attr_5=slot_values['num_attr_5']
                    )
                    created_count += 1
                    
            return JsonResponse({'status': 'success', 'created_count': created_count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

def mm_batch_delete(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mat_ids = data.get('mat_ids', [])
            if not mat_ids:
                return JsonResponse({'status': 'error', 'message': 'No IDs provided.'}, status=400)
            
            deleted_count, _ = MetalMaterial.objects.filter(id__in=mat_ids).delete()
            return JsonResponse({'status': 'success', 'deleted_count': deleted_count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
