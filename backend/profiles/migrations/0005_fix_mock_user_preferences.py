# Data migration to fix mock users' looking_for preferences
from django.db import migrations


def fix_mock_user_preferences(apps, schema_editor):
    """Fix mock users that have empty gender preferences."""
    Profile = apps.get_model('profiles', 'Profile')
    LookingFor = apps.get_model('profiles', 'LookingFor')
    
    # Gender mapping for what each gender typically looks for
    gender_prefs = {
        'male': ['women'],
        'female': ['men'],
        'nonbinary': ['men', 'women', 'nonbinary'],
    }
    
    for profile in Profile.objects.filter(user__username__startswith='mock_'):
        try:
            lf = LookingFor.objects.get(profile=profile)
            if not lf.genders:  # Empty genders list
                lf.genders = gender_prefs.get(profile.gender, ['men', 'women'])
                lf.save()
        except LookingFor.DoesNotExist:
            LookingFor.objects.create(
                profile=profile,
                genders=gender_prefs.get(profile.gender, ['men', 'women']),
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
