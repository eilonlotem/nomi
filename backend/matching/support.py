"""
Support user ("תמיכה") — a built-in avatar that every new user is
automatically matched with. The admin responds to messages via Django admin.
"""
from __future__ import annotations

import logging
from typing import Optional

from django.db import transaction
from django.db.models import Q

from users.models import User

logger = logging.getLogger(__name__)

SUPPORT_USERNAME = "support_nomi"
SUPPORT_DISPLAY_NAME = "תמיכה"
SUPPORT_DISPLAY_NAME_EN = "Support"
SUPPORT_BIO_HE = "היי! אני כאן כדי לעזור לך עם כל שאלה על האפליקציה. שלח/י הודעה ואחזור אליך בהקדם 💜"
SUPPORT_BIO_EN = "Hi! I'm here to help you with any questions about the app. Send a message and I'll get back to you soon 💜"

WELCOME_MESSAGE_HE = "היי! ברוך/ה הבא/ה לנומי 💜\nאני כאן כדי לעזור לך עם כל שאלה. אל תהסס/י לשלוח הודעה!"
WELCOME_MESSAGE_EN = "Hi! Welcome to Nomi 💜\nI'm here to help you with any questions. Don't hesitate to send a message!"


def get_or_create_support_user() -> User:
    """Return the singleton support user, creating it if needed."""
    from profiles.models import Profile

    user = User.objects.filter(username=SUPPORT_USERNAME).first()
    if user:
        return user

    with transaction.atomic():
        user = User.objects.create_user(
            username=SUPPORT_USERNAME,
            email="support@nomi.app",
            password=None,
            first_name="תמיכה",
            last_name="",
        )
        user.is_onboarded = True
        user.is_profile_complete = True
        user.is_verified = True
        user.save()

        Profile.objects.create(
            user=user,
            display_name=SUPPORT_DISPLAY_NAME,
            bio=SUPPORT_BIO_HE,
            gender="prefer_not_to_say",
            city="",
            is_visible=False,
            picture_url="",
        )

    logger.info("Created support user: %s", SUPPORT_USERNAME)
    return user


def ensure_support_match(user: User) -> None:
    """
    Create a match, conversation, and welcome message between *user* and the
    support avatar. Safe to call multiple times — it's a no-op when the match
    already exists.
    """
    from .models import Conversation, Match, Message

    if user.username == SUPPORT_USERNAME:
        return

    support_user = get_or_create_support_user()

    existing = Match.objects.filter(
        Q(user1=user, user2=support_user) | Q(user1=support_user, user2=user)
    ).first()

    if existing:
        return

    with transaction.atomic():
        match = Match.objects.create(
            user1=support_user,
            user2=user,
            compatibility_score=100,
            is_active=True,
        )

        conversation = Conversation.objects.create(match=match)

        lang = getattr(user, "preferred_language", "he")
        welcome = WELCOME_MESSAGE_HE if lang == "he" else WELCOME_MESSAGE_EN

        Message.objects.create(
            conversation=conversation,
            sender=support_user,
            content=welcome,
        )

    logger.info("Created support match for user %s", user.username)
