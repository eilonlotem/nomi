from __future__ import annotations

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_support_match_for_new_user(
    sender: type, instance: User, created: bool, **kwargs: object
) -> None:
    """Ensure every newly created user gets matched with the support avatar."""
    if not created:
        return

    try:
        from matching.support import SUPPORT_USERNAME, ensure_support_match

        if instance.username == SUPPORT_USERNAME:
            return

        ensure_support_match(instance)
    except Exception:
        logger.exception("Failed to create support match for %s", instance.username)
