"""
Management command to create (or verify) the support avatar user.

Usage:
    python manage.py create_support_user

Safe to run multiple times — idempotent.
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from matching.support import SUPPORT_USERNAME, get_or_create_support_user


class Command(BaseCommand):
    help = "Create the support avatar user (תמיכה) if it does not exist"

    def handle(self, *args: Any, **options: Any) -> None:
        user = get_or_create_support_user()
        self.stdout.write(
            self.style.SUCCESS(
                f"Support user ready: {SUPPORT_USERNAME} (id={user.id})"
            )
        )
