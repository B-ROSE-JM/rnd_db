import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rnd_platform.settings')
django.setup()

from materials.models import Material
from om.models import OrganicMaterial, OMImage, OMRawData
from mm.models import MetalMaterial, MMImage, MMRawData

def run_migration():
    print("Starting data migration...")
    
    materials = Material.objects.all()
    for mat in materials:
        if mat.name.lower() in ['copper']:
            # Migrate to MM
            new_mat = MetalMaterial.objects.create(
                name=mat.name,
                material_type=mat.material_type,
                custom_attributes=mat.custom_attributes,
                created_at=mat.created_at,
                updated_at=mat.updated_at
            )
            
            for img in mat.images.all():
                MMImage.objects.create(
                    material=new_mat,
                    image=img.image,
                    description=img.description,
                    uploaded_at=img.uploaded_at
                )
                
            for raw in mat.raw_files.all():
                MMRawData.objects.create(
                    material=new_mat,
                    file=raw.file,
                    description=raw.description,
                    uploaded_at=raw.uploaded_at
                )
            print(f"Migrated {mat.name} to MM")
            
        else:
            # Migrate to OM
            new_mat = OrganicMaterial.objects.create(
                name=mat.name,
                material_type=mat.material_type,
                custom_attributes=mat.custom_attributes,
                created_at=mat.created_at,
                updated_at=mat.updated_at
            )
            
            for img in mat.images.all():
                OMImage.objects.create(
                    material=new_mat,
                    image=img.image,
                    description=img.description,
                    uploaded_at=img.uploaded_at
                )
                
            for raw in mat.raw_files.all():
                OMRawData.objects.create(
                    material=new_mat,
                    file=raw.file,
                    description=raw.description,
                    uploaded_at=raw.uploaded_at
                )
            print(f"Migrated {mat.name} to OM")
            
    print("Migration complete!")

if __name__ == '__main__':
    run_migration()
