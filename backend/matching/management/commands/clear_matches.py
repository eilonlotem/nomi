"""Management command to clear all matching-related data."""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from matching.models import Match, Swipe, Message, Conversation


class Command(BaseCommand):
    """Clear all matches, swipes, messages, and conversations."""

    help = "Clear all matching-related data (matches, swipes, messages, conversations)"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm deletion without prompting",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  This will delete ALL matches, swipes, messages, and conversations!"
                )
            )
            self.stdout.write("Run with --confirm to proceed.")
            return

        self.stdout.write("🧹 Clearing matching data...")

        # Delete in order (messages first due to foreign keys)
        message_count = Message.objects.count()
        Message.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {message_count} messages")

        conversation_count = Conversation.objects.count()
        Conversation.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {conversation_count} conversations")

        match_count = Match.objects.count()
        Match.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {match_count} matches")

        swipe_count = Swipe.objects.count()
        Swipe.objects.all().delete()
        self.stdout.write(f"  ✓ Deleted {swipe_count} swipes")

        self.stdout.write(
            self.style.SUCCESS("✅ All matching data cleared successfully!")
        )
