from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models


class DisabilityTag(models.Model):
    """Predefined disability/identity tags users can select."""

    code = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=100)
    name_he = models.CharField(max_length=100, blank=True)
    name_es = models.CharField(max_length=100, blank=True)
    name_fr = models.CharField(max_length=100, blank=True)
    name_ar = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name_en"]

    def __str__(self) -> str:
        return self.name_en

    def get_name(self, language: str = "en") -> str:
        """Get localized name."""
        return getattr(self, f"name_{language}", self.name_en) or self.name_en


class Interest(models.Model):
    """Predefined interests users can select."""

    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=10, blank=True)
    category = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name


class Profile(models.Model):
    """
    Extended profile for Nomi users.
    One-to-one relationship with User model.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Basic info
    display_name = models.CharField(max_length=100)
    bio = models.TextField(max_length=500, blank=True)
    
    # Date of birth and age
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Gender
    GENDER_CHOICES: list[tuple[str, str]] = [
        ("male", "Male"),
        ("female", "Female"),
        ("nonbinary", "Non-binary"),
        ("other", "Other"),
        ("prefer_not_to_say", "Prefer not to say"),
    ]
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    
    # Profile picture from social login
    picture_url = models.URLField(max_length=500, blank=True)

    # Location
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Identity & Disability tags
    disability_tags = models.ManyToManyField(
        DisabilityTag, blank=True, related_name="profiles"
    )

    # Interests
    interests = models.ManyToManyField(Interest, blank=True, related_name="profiles")

    # Current mood/energy
    MOOD_CHOICES: list[tuple[str, str]] = [
        ("lowEnergy", "Low Energy"),
        ("open", "Open to Connect"),
        ("chatty", "Ready to Chat"),
        ("adventurous", "Feeling Bold"),
    ]
    current_mood = models.CharField(
        max_length=20,
        choices=MOOD_CHOICES,
        default="open",
    )

    # Profile prompts
    PROMPT_CHOICES: list[tuple[str, str]] = [
        ("laughMost", "The thing that makes me laugh most is..."),
        ("perfectSunday", "My perfect Sunday looks like..."),
        ("convinced", "I'm convinced that..."),
    ]
    prompt_id = models.CharField(max_length=50, choices=PROMPT_CHOICES, blank=True)
    prompt_answer = models.CharField(max_length=300, blank=True)

    # Visibility
    is_visible = models.BooleanField(default=True)
    show_distance = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self) -> str:
        return f"{self.display_name}'s Profile"


class ProfilePhoto(models.Model):
    """Photos for user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    image = models.ImageField(upload_to="profile_photos/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-is_primary"]

    def __str__(self) -> str:
        return f"Photo for {self.profile.display_name}"

    def save(self, *args: Any, **kwargs: Any) -> None:
        # Ensure only one primary photo per profile
        if self.is_primary:
            ProfilePhoto.objects.filter(
                profile=self.profile,
                is_primary=True,
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class LookingFor(models.Model):
    """User's dating preferences."""

    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name="looking_for",
    )

    # Gender preferences
    GENDER_CHOICES: list[tuple[str, str]] = [
        ("men", "Men"),
        ("women", "Women"),
        ("nonbinary", "Non-binary"),
        ("everyone", "Everyone"),
    ]
    genders = models.JSONField(default=list)  # List of gender codes

    # Relationship type
    RELATIONSHIP_CHOICES: list[tuple[str, str]] = [
        ("casual", "Casual Dating"),
        ("serious", "Serious Relationship"),
        ("friends", "Just Friends"),
        ("activity", "Activity Partners"),
    ]
    relationship_types = models.JSONField(default=list)  # List of relationship codes

    # Age range
    min_age = models.PositiveIntegerField(default=18)
    max_age = models.PositiveIntegerField(default=50)

    # Location preferences
    max_distance = models.PositiveIntegerField(default=50)  # in km
    preferred_location = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Looking For Preferences"
        verbose_name_plural = "Looking For Preferences"

    def __str__(self) -> str:
        return f"{self.profile.display_name}'s Preferences"
