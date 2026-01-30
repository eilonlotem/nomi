from __future__ import annotations

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0007_add_url_to_profilephoto"),
    ]

    operations = [
        migrations.AddField(
            model_name="disabilitytag",
            name="category",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="disabilitytag",
            name="disclosure_level",
            field=models.CharField(
                choices=[
                    ("functional", "Functional Description"),
                    ("diagnosis", "Diagnosis/Condition"),
                ],
                default="functional",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="relationship_intent",
            field=models.CharField(
                blank=True,
                choices=[
                    ("relationship", "Looking for a relationship"),
                    ("friendship", "Looking for friends"),
                    ("open", "Open to anything"),
                    ("slow", "Prefer a calm introduction"),
                    ("unsure", "Not sure yet"),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="openness_tags",
            field=models.JSONField(default=list),
        ),
        migrations.CreateModel(
            name="ProfileDisabilityTagVisibility",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("public", "Visible to everyone"),
                            ("matches", "Visible to matches only"),
                            ("specific", "Visible to specific users"),
                            ("hidden", "Hidden"),
                        ],
                        default="public",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tag_visibilities",
                        to="profiles.profile",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile_visibilities",
                        to="profiles.disabilitytag",
                    ),
                ),
                (
                    "allowed_viewers",
                    models.ManyToManyField(
                        blank=True,
                        related_name="visible_disability_tags",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "unique_together": {("profile", "tag")},
            },
        ),
    ]
