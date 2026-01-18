# Data migration to unify gender preference values (men->male, women->female)
from django.db import migrations


def unify_gender_values(apps, schema_editor):
    """Convert old men/women preference values to unified male/female."""
    LookingFor = apps.get_model('profiles', 'LookingFor')
    
    # Value mapping: old -> new
    value_map = {'men': 'male', 'women': 'female'}
    
    for lf in LookingFor.objects.all():
        if not lf.genders:
            continue
            
        new_genders = []
        changed = False
        
        for g in lf.genders:
            if g in value_map:
                new_genders.append(value_map[g])
                changed = True
            else:
                new_genders.append(g)
        
        if changed:
            lf.genders = new_genders
            lf.save()


def reverse_unify(apps, schema_editor):
    """Reverse: convert male/female back to men/women."""
    LookingFor = apps.get_model('profiles', 'LookingFor')
    
    value_map = {'male': 'men', 'female': 'women'}
    
    for lf in LookingFor.objects.all():
        if not lf.genders:
            continue
            
        new_genders = []
        changed = False
        
        for g in lf.genders:
            if g in value_map:
                new_genders.append(value_map[g])
                changed = True
            else:
                new_genders.append(g)
        
        if changed:
            lf.genders = new_genders
            lf.save()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_fix_mock_user_preferences'),
    ]

    operations = [
        migrations.RunPython(unify_gender_values, reverse_unify),
    ]
