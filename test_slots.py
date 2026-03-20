import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rnd_platform.settings')
django.setup()

from materials.models import SearchSlotConfig
from mm.models import MetalMaterial
from om.models import OrganicMaterial

def test():
    # Setup config
    mm_config, _ = SearchSlotConfig.objects.get_or_create(category='mm')
    mm_config.slot_1_name = '밀도'
    mm_config.slot_2_name = '점도'
    mm_config.save()
    
    print("SearchSlotConfig updated successfully.")
    
    # Test mm_add logic simulation
    keys = ['밀도 ', ' 점도', '색상', '순도']
    values = ['5.5', '100', '빨강', '99.9']
    
    from mm.views import _parse_slots
    custom_attrs, slot_values = _parse_slots(mm_config, keys, values)
    
    print(f"Parsed Custom: {custom_attrs}")
    print(f"Parsed Slots: {slot_values}")
    
    assert slot_values['num_attr_1'] == 5.5, "밀도 should map to num_attr_1"
    assert slot_values['num_attr_2'] == 100.0, "점도 should map to num_attr_2"
    assert custom_attrs['색상'] == '빨강', "색상 should be in custom_attrs"
    assert custom_attrs['순도'] == '99.9', "순도 should be in custom_attrs"
    print("Slot logic tests PASSED.")

if __name__ == '__main__':
    test()
