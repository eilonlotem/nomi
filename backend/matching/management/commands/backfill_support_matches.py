"""
One-time command to create the support match for all existing users
who don't have one yet.

Usage:
    python manage.py backfill_support_matches
"""
from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from matching.support import SUPPORT_USERNAME, ensure_support_match

User = get_user_model()


class Command(BaseCommand):
    help = "Create a support match + welcome message for every existing user"

    def handle(self, *args: Any, **options: Any) -> None:
        users = User.objects.exclude(username=SUPPORT_USERNAME)
        total = users.count()
        created = 0

        for user in users.iterator():
            try:
                ensure_support_match(user)
                created += 1
            except Exception as exc:
                self.stderr.write(f"  Failed for {user.username}: {exc}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done — processed {total} users, ensured {created} support matches."
            )
        )
