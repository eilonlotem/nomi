# Change audio_url from URLField to CharField to support both URLs and local paths

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matching", "0006_message_transcript"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="audio_url",
            field=models.CharField(max_length=500, blank=True, null=True),
        ),
    ]
