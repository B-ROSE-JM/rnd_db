from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Material, MaterialImage, MaterialRawData

def material_list(request):
    materials = Material.objects.prefetch_related('images', 'raw_files').all().order_by('-created_at')
    
    # Extract unique keys from all custom_attributes to build dynamic table headers
    custom_keys = set()
    for mat in materials:
        if isinstance(mat.custom_attributes, dict):
            custom_keys.update(mat.custom_attributes.keys())
    
    custom_keys = sorted(list(custom_keys))
    
    return render(request, 'materials/list.html', {
        'materials': materials,
        'custom_keys': custom_keys
    })

def material_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        material_type = request.POST.get('material_type')
        
        # Handle dynamic custom attributes
        custom_attrs = {}
        keys = request.POST.getlist('custom_keys[]')
        values = request.POST.getlist('custom_values[]')
        
        for k, v in zip(keys, values):
            if k.strip() and v.strip():
                custom_attrs[k.strip()] = v.strip()
                
        material = Material.objects.create(
            name=name,
            material_type=material_type,
            custom_attributes=custom_attrs
        )
        
        # Process multiple images
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            MaterialImage.objects.create(material=material, image=img, description=desc)
            
        # Process multiple raw data files
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            MaterialRawData.objects.create(material=material, file=r_file, description=desc)
        
        messages.success(request, 'Material successfully created with custom attributes and files.')
        return redirect('materials:list')
        
    # Get previously used keys for pre-population
    all_keys = set()
    for mat in Material.objects.all():
        if isinstance(mat.custom_attributes, dict):
            all_keys.update(mat.custom_attributes.keys())
            
    custom_fields = []
    for k in sorted(list(all_keys)):
        custom_fields.append({'key': k, 'val': ''})
    
    # Get distinct material types for datalist
    existing_types = list(Material.objects.values_list('material_type', flat=True).distinct().order_by('material_type'))
    
    return render(request, 'materials/form.html', {
        'custom_fields': custom_fields,
        'existing_types': existing_types
    })

def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)

    if request.method == 'POST':
        material.name = request.POST.get('name')
        material.material_type = request.POST.get('material_type')
        
        # Handle dynamic custom attributes
        custom_attrs = {}
        keys = request.POST.getlist('custom_keys[]')
        values = request.POST.getlist('custom_values[]')
        for k, v in zip(keys, values):
            if k.strip() and v.strip():
                custom_attrs[k.strip()] = v.strip()
        material.custom_attributes = custom_attrs
        
        material.save()
        
        # Handle file deletions
        images_to_delete = request.POST.getlist('delete_image_ids[]')
        if images_to_delete:
            MaterialImage.objects.filter(id__in=images_to_delete, material=material).delete()
            
        raw_to_delete = request.POST.getlist('delete_raw_ids[]')
        if raw_to_delete:
            MaterialRawData.objects.filter(id__in=raw_to_delete, material=material).delete()
            
        # Process multiple images
        images = request.FILES.getlist('image_files')
        image_descs = request.POST.getlist('image_descs[]')
        for i, img in enumerate(images):
            desc = image_descs[i].strip() if i < len(image_descs) else ''
            MaterialImage.objects.create(material=material, image=img, description=desc)
            
        # Process multiple raw data files
        raw_files = request.FILES.getlist('raw_data_files')
        raw_data_descs = request.POST.getlist('raw_data_descs[]')
        for i, r_file in enumerate(raw_files):
            desc = raw_data_descs[i].strip() if i < len(raw_data_descs) else ''
            MaterialRawData.objects.create(material=material, file=r_file, description=desc)
        
        messages.success(request, 'Material successfully updated.')
        return redirect('materials:list')
        
    # Get previously used keys for pre-population
    all_keys = set()
    for mat in Material.objects.all():
        if isinstance(mat.custom_attributes, dict):
            all_keys.update(mat.custom_attributes.keys())
            
    custom_fields = []
    for k in sorted(list(all_keys)):
        val = material.custom_attributes.get(k, '') if isinstance(material.custom_attributes, dict) else ''
        custom_fields.append({'key': k, 'val': val})
    
    existing_types = list(Material.objects.values_list('material_type', flat=True).distinct().order_by('material_type'))
    
    # Pre-render existing files HTML to avoid VSCode formatter breaking template tags
    existing_images_html = ''
    for i, img in enumerate(material.images.all()):
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
    for rf in material.raw_files.all():
        existing_raw_html += (
            '<div style="display: flex; gap: 12px; align-items: center; padding: 8px; '
            'border: 1px solid var(--border-color); border-radius: 6px; background-color: white;">'
            '<i class="fas fa-file-csv" style="color: #10B981; font-size: 1.5rem;"></i>'
            '<span style="flex: 1; font-size: 0.875rem; color: var(--text-main);">{}</span>'
            '<label style="color: #EF4444; font-size: 0.875rem; display: flex; align-items: center; gap: 4px; cursor: pointer;">'
            '<input type="checkbox" name="delete_raw_ids[]" value="{}"> Delete'
            '</label></div>'
        ).format(rf.file.name, rf.id)
            
    return render(request, 'materials/form.html', {
        'material': material,
        'custom_fields': custom_fields,
        'existing_types': existing_types,
        'existing_images_html': existing_images_html,
        'existing_raw_html': existing_raw_html
    })
