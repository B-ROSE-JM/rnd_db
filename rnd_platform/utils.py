import os
import shutil
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

def validate_file_size(file):
    max_size_kb = 50 * 1024
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"파일 크기는 50MB를 초과할 수 없습니다. (현재: {file.size / (1024 * 1024):.2f}MB)")

def get_mm_raw_data_path(instance, filename):
    mat_id = instance.material.id if instance.material else 'new'
    date_str = timezone.now().strftime('%Y-%m-%d')
    return f'mm/raw_data/{mat_id}_{date_str}/mat_{mat_id}_{filename}'

def get_mm_image_path(instance, filename):
    mat_id = instance.material.id if instance.material else 'new'
    date_str = timezone.now().strftime('%Y-%m-%d')
    return f'mm/images/{mat_id}_{date_str}/mat_{mat_id}_{filename}'

def get_om_raw_data_path(instance, filename):
    mat_id = instance.material.id if instance.material else 'new'
    date_str = timezone.now().strftime('%Y-%m-%d')
    return f'om/raw_data/{mat_id}_{date_str}/mat_{mat_id}_{filename}'

def get_om_image_path(instance, filename):
    mat_id = instance.material.id if instance.material else 'new'
    date_str = timezone.now().strftime('%Y-%m-%d')
    return f'om/images/{mat_id}_{date_str}/mat_{mat_id}_{filename}'

def move_file_to_trash(file_field, app_name, subfolder):
    """
    Moves a file to the media/trash/ directory while retaining its name.
    """
    if not file_field or not file_field.name:
        return
        
    storage = file_field.storage
    if not storage.exists(file_field.name):
        return

    source_path = storage.path(file_field.name)
    if not os.path.exists(source_path):
        return
        
    trash_dir = os.path.join(settings.MEDIA_ROOT, 'trash', app_name, subfolder)
    os.makedirs(trash_dir, exist_ok=True)
    
    filename = os.path.basename(source_path)
    trash_path = os.path.join(trash_dir, filename)
    
    # Handle filename collision in trash
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(trash_path):
        trash_path = os.path.join(trash_dir, f"{base}_{counter}{ext}")
        counter += 1
        
    try:
        shutil.move(source_path, trash_path)
    except Exception as e:
        print(f"Error moving file to trash: {e}")
