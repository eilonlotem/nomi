# Generated manually for custom shortcut responses

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("matching", "0004_shortcut_response"),
    ]

    operations = [
        migrations.AddField(
            model_name="shortcutresponse",
            name="title",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shortcutresponse",
            name="content",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="shortcutresponse",
            unique_together={("user", "title")},
        ),
        migrations.RemoveField(
            model_name="shortcutresponse",
            name="shortcut_key",
        ),
    ]

