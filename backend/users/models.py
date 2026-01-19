from __future__ import annotations

from datetime import date
from typing import Optional, TYPE_CHECKING

from django.contrib.auth.models import AbstractUser
from django.db import models

if TYPE_CHECKING:
    from django.db.models import Manager


class User(AbstractUser):
    """
    Custom User model for Nomi dating app.
    Extends Django's AbstractUser to add social auth and app-specific fields.
    """

    # Social authentication
    SOCIAL_PROVIDER_CHOICES: list[tuple[str, str]] = [
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
    ]

    social_provider = models.CharField(
        max_length=20,
        choices=SOCIAL_PROVIDER_CHOICES,
        blank=True,
        null=True,
    )
    social_id = models.CharField(max_length=255, blank=True, null=True, unique=True)

    # Profile basics
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Preferences
    LANGUAGE_CHOICES: list[tuple[str, str]] = [
        ("en", "English"),
        ("he", "Hebrew"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("ar", "Arabic"),
    ]

    preferred_language = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default="he",  # Hebrew is the default language
    )

    # Account status
    is_verified = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)  # True after completing onboarding

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email or self.username

    @property
    def age(self) -> Optional[int]:
        """Calculate user's age from date of birth."""
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


class Invitation(models.Model):
    """
    Model to track invitations sent by users to their Facebook friends.
    """

    STATUS_CHOICES: list[tuple[str, str]] = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("expired", "Expired"),
    ]

    # The user who sent the invitation
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )

    # Facebook ID of the invited friend (they might not be a user yet)
    facebook_friend_id = models.CharField(max_length=255)
    facebook_friend_name = models.CharField(max_length=255, blank=True)

    # If the invited friend joins, link to their user account
    invited_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="received_invitations",
        blank=True,
        null=True,
    )

    # Status of the invitation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Invitation"
        verbose_name_plural = "Invitations"
        ordering = ["-created_at"]
        # Prevent duplicate invitations from the same sender to the same friend
        unique_together = ["sender", "facebook_friend_id"]

    def __str__(self) -> str:
        return f"{self.sender.username} invited {self.facebook_friend_name or self.facebook_friend_id}"
