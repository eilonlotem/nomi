from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django.conf import settings
from django.db import models
from django.db.models import Q

if TYPE_CHECKING:
    from users.models import User


class Swipe(models.Model):
    """Records user swipes (pass/like/super-like)."""

    SWIPE_CHOICES: list[tuple[str, str]] = [
        ("pass", "Pass"),
        ("like", "Like"),
        ("super", "Super Like"),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="swipes_made",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="swipes_received",
    )
    action = models.CharField(max_length=10, choices=SWIPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["from_user", "to_user"]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.from_user} -> {self.to_user}: {self.action}"


class Match(models.Model):
    """
    Represents a mutual match between two users.
    Created when both users like each other.
    """

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user1",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matches_as_user2",
    )

    # Match metadata
    matched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Compatibility score (calculated at match time)
    compatibility_score = models.PositiveIntegerField(default=0)
    shared_tags_count = models.PositiveIntegerField(default=0)
    shared_interests_count = models.PositiveIntegerField(default=0)
    
    # Full compatibility breakdown stored as JSON
    compatibility_breakdown = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ["user1", "user2"]
        ordering = ["-matched_at"]
        verbose_name = "Match"
        verbose_name_plural = "Matches"

    def __str__(self) -> str:
        return f"Match: {self.user1} & {self.user2}"

    @staticmethod
    def get_match_between(user1: User, user2: User) -> Optional[Match]:
        """Get match between two users, regardless of order."""
        return Match.objects.filter(
            Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
        ).first()


class Conversation(models.Model):
    """Chat conversation between matched users."""

    match = models.OneToOneField(
        Match,
        on_delete=models.CASCADE,
        related_name="conversation",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"Conversation for {self.match}"

    @property
    def last_message(self) -> Optional[Message]:
        return self.messages.order_by("-sent_at").first()


class Message(models.Model):
    """Individual messages in a conversation."""

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="messages_sent",
    )

    # Message content
    MESSAGE_TYPE_CHOICES: list[tuple[str, str]] = [
        ("text", "Text"),
        ("voice", "Voice Note"),
        ("image", "Image"),
        ("icebreaker", "Icebreaker"),
    ]
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default="text",
    )
    content = models.TextField()

    # For voice notes
    audio_url = models.URLField(blank=True, null=True)
    audio_duration = models.PositiveIntegerField(null=True, blank=True)  # seconds

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self) -> str:
        return f"Message from {self.sender} at {self.sent_at}"

    def mark_as_read(self) -> None:
        if not self.is_read:
            from django.utils import timezone

            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class Block(models.Model):
    """Block/report functionality."""

    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_made",
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_received",
    )

    REASON_CHOICES: list[tuple[str, str]] = [
        ("spam", "Spam"),
        ("inappropriate", "Inappropriate Content"),
        ("harassment", "Harassment"),
        ("fake", "Fake Profile"),
        ("other", "Other"),
    ]
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, blank=True)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["blocker", "blocked"]

    def __str__(self) -> str:
        return f"{self.blocker} blocked {self.blocked}"
