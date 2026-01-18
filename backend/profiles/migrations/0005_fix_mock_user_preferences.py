# Data migration to fix mock users' looking_for preferences
from django.db import migrations


def fix_mock_user_preferences(apps, schema_editor):
    """Fix all users that have incorrect or empty gender preferences.
    
    We now use unified values: male/female/nonbinary for both profile.gender
    and looking_for.genders. This migration converts any old 'men'/'women' 
    values to 'male'/'female'.
    """
    Profile = apps.get_model('profiles', 'Profile')
    LookingFor = apps.get_model('profiles', 'LookingFor')
    
    # Gender mapping for what each gender typically looks for (using unified values)
    gender_prefs = {
        'male': ['female'],
        'female': ['male'],
        'nonbinary': ['male', 'female', 'nonbinary'],
    }
    
    # Value mapping (fix old men/women values to unified male/female)
    value_map = {'men': 'male', 'women': 'female'}
    
    # Fix ALL LookingFor records
    for lf in LookingFor.objects.all():
        changed = False
        new_genders = []
        
        # Fix old values (men->male, women->female)
        for g in (lf.genders or []):
            if g in value_map:
                new_genders.append(value_map[g])
                changed = True
            else:
                new_genders.append(g)
        
        # Fix empty preferences based on profile gender
        if not new_genders:
            profile_gender = lf.profile.gender
            new_genders = gender_prefs.get(profile_gender, ['male', 'female'])
            changed = True
        
        if changed:
            lf.genders = new_genders
            lf.save()
    
    # Create LookingFor for profiles that don't have one
    for profile in Profile.objects.filter(user__username__startswith='mock_'):
        if not LookingFor.objects.filter(profile=profile).exists():
            LookingFor.objects.create(
                profile=profile,
                genders=gender_prefs.get(profile.gender, ['male', 'female']),
                min_age=18,
                max_age=50,
                max_distance=100,
                relationship_types=['serious'],
            )


def reverse_fix(apps, schema_editor):
    pass  # No reverse needed


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_add_time_preferences_and_ask_me'),
    ]

    operations = [
        migrations.RunPython(fix_mock_user_preferences, reverse_fix),
    ]
