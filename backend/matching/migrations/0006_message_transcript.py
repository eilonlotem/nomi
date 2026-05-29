# Generated for speech-to-text transcript on voice messages

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matching", "0005_shortcut_response_custom"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="transcript",
            field=models.TextField(blank=True, default=""),
        ),
    ]
