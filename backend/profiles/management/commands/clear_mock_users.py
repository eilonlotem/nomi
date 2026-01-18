"""
Management command to clear all mock users.
Run this before seed_mock_users to refresh mock user profiles.
Usage: python manage.py clear_mock_users
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from profiles.models import Profile

User = get_user_model()

MOCK_USER_PREFIX = "mock_"


class Command(BaseCommand):
    help = "Clear all mock users from the database"

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        mock_users = User.objects.filter(username__startswith=MOCK_USER_PREFIX)
        count = mock_users.count()

        if count == 0:
            self.stdout.write(self.style.WARNING("No mock users found."))
            return

        if not options["yes"]:
            confirm = input(f"Delete {count} mock users? [y/N]: ")
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        with transaction.atomic():
            # Delete profiles first (cascades to related models)
            Profile.objects.filter(user__username__startswith=MOCK_USER_PREFIX).delete()
            # Delete users
            mock_users.delete()

        self.stdout.write(
            self.style.SUCCESS(f"✅ Deleted {count} mock users.")
        )
        self.stdout.write(
            "Run 'python manage.py seed_mock_users' to recreate them with updated content."
        )
