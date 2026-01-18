# Generated manually for matching algorithm feature

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matching', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='shared_interests_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='match',
            name='compatibility_breakdown',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
