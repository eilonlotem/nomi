from __future__ import annotations

from typing import Any

from django.conf import settings
from django.db import models


class DisabilityTag(models.Model):
    """Predefined disability/identity tags users can select."""

    DISCLOSURE_LEVEL_CHOICES: list[tuple[str, str]] = [
        ("functional", "Functional Description"),
        ("diagnosis", "Diagnosis/Condition"),
    ]

    code = models.CharField(max_length=50, unique=True)
    name_en = models.CharField(max_length=100)
    name_he = models.CharField(max_length=100, blank=True)
    name_es = models.CharField(max_length=100, blank=True)
    name_fr = models.CharField(max_length=100, blank=True)
    name_ar = models.CharField(max_length=100, blank=True)
    icon = models.CharField(max_length=10)
    category = models.CharField(max_length=50, blank=True)
    disclosure_level = models.CharField(
        max_length=20,
        choices=DISCLOSURE_LEVEL_CHOICES,
        default="functional",
    )
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

    # Relationship intent (what I'm looking for)
    RELATIONSHIP_INTENT_CHOICES: list[tuple[str, str]] = [
        ("relationship", "Looking for a relationship"),
        ("friendship", "Looking for friends"),
        ("open", "Open to anything"),
        ("slow", "Prefer a calm introduction"),
        ("unsure", "Not sure yet"),
    ]
    relationship_intent = models.CharField(
        max_length=30,
        choices=RELATIONSHIP_INTENT_CHOICES,
        blank=True,
    )

    # Openness tags (who I'm open to connect with)
    openness_tags = models.JSONField(default=list)

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

    # "Ask Me About It" - Celebration prompts about disability
    ASK_ME_PROMPT_CHOICES: list[tuple[str, str]] = [
        ("coolestThing", "The coolest thing about my [disability/difference] is..."),
        ("superpower", "My superpower from being [neurodivergent/disabled] is..."),
        ("wishPeopleKnew", "What I wish people knew about [my condition] is..."),
        ("proudOf", "Something I'm proud of overcoming is..."),
        ("dontLetStop", "I don't let my [condition] stop me from..."),
        ("loveAboutCommunity", "What I love about the disability community is..."),
    ]
    ask_me_prompt_id = models.CharField(max_length=50, blank=True)
    ask_me_answer = models.CharField(max_length=300, blank=True)

    # Time Preferences - Best times for dates/meetings
    TIME_PREFERENCE_CHOICES: list[tuple[str, str]] = [
        ("morning", "Morning (before noon)"),
        ("afternoon", "Afternoon (noon-5pm)"),
        ("evening", "Evening (5pm-9pm)"),
        ("night", "Night (after 9pm)"),
        ("flexible", "I'm flexible"),
    ]
    preferred_times = models.JSONField(default=list)  # List of time preference codes
    
    # Additional time-related preferences
    response_pace = models.CharField(
        max_length=50,
        choices=[
            ("quick", "I respond quickly"),
            ("moderate", "I respond within a few hours"),
            ("slow", "I may take a day or more to respond"),
            ("variable", "It depends on my energy/health"),
        ],
        blank=True,
    )
    date_pace = models.CharField(
        max_length=50,
        choices=[
            ("ready", "Ready to meet soon"),
            ("slow", "Prefer to chat first"),
            ("virtual", "Virtual dates preferred"),
            ("flexible", "Open to whatever feels right"),
        ],
        blank=True,
    )
    time_notes = models.CharField(
        max_length=200,
        blank=True,
        help_text="Additional notes about scheduling (e.g., 'I have PT on Tuesdays')",
    )

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
    image = models.ImageField(upload_to="profile_photos/", blank=True)
    # URL field for external images (e.g., from Unsplash for mock data)
    url = models.URLField(max_length=500, blank=True)
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


class ProfileDisabilityTagVisibility(models.Model):
    """Visibility controls for disability tags per profile."""

    VISIBILITY_CHOICES: list[tuple[str, str]] = [
        ("public", "Visible to everyone"),
        ("matches", "Visible to matches only"),
        ("specific", "Visible to specific users"),
        ("hidden", "Hidden"),
    ]

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="tag_visibilities",
    )
    tag = models.ForeignKey(
        DisabilityTag,
        on_delete=models.CASCADE,
        related_name="profile_visibilities",
    )
    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="public",
    )
    allowed_viewers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="visible_disability_tags",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["profile", "tag"]
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.profile.display_name}: {self.tag.code} ({self.visibility})"


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
