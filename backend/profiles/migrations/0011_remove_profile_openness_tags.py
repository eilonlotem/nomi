from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0010_remove_profile_date_pace"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="openness_tags",
        ),
    ]
