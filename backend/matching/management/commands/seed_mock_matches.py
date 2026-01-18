"""
Management command to seed mock matches between mock users.
This creates sample matches and conversations for demo purposes.
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from matching.models import Swipe, Match, Conversation, Message


User = get_user_model()

# Mock user prefix
MOCK_USER_PREFIX = "mock_"

# Predefined matches between mock users (pairs of usernames)
MOCK_MATCHES = [
    ("mock_maya", "mock_daniel"),
    ("mock_noa", "mock_alex"),
    ("mock_sarah", "mock_yossi"),
    ("mock_emma", "mock_amit"),
]

# Sample messages for conversations
SAMPLE_MESSAGES = [
    ("Hey! I loved your profile 😊", 0),
    ("Thanks! Your photos are amazing!", 1),
    ("What's your favorite thing to do on weekends?", 0),
    ("I love going to coffee shops and reading. You?", 1),
]


class Command(BaseCommand):
    help = "Seed mock matches between mock users (idempotent)"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("💕 Seeding mock matches...")
        
        created_matches = 0
        created_conversations = 0
        
        with transaction.atomic():
            for user1_name, user2_name in MOCK_MATCHES:
                user1 = User.objects.filter(username=user1_name).first()
                user2 = User.objects.filter(username=user2_name).first()
                
                if not user1 or not user2:
                    self.stdout.write(f"  ⚠️ Skipping {user1_name} <-> {user2_name}: user not found")
                    continue
                
                # Check if match already exists
                existing_match = Match.objects.filter(
                    user1__in=[user1, user2],
                    user2__in=[user1, user2],
                ).first()
                
                if existing_match:
                    self.stdout.write(f"  🔄 Match exists: {user1_name} <-> {user2_name}")
                    continue
                
                # Create mutual swipes
                Swipe.objects.get_or_create(
                    from_user=user1,
                    to_user=user2,
                    defaults={"action": "like"}
                )
                Swipe.objects.get_or_create(
                    from_user=user2,
                    to_user=user1,
                    defaults={"action": "like"}
                )
                
                # Create match
                match = Match.objects.create(
                    user1=user1,
                    user2=user2,
                    compatibility_score=75,
                    shared_tags_count=2,
                )
                created_matches += 1
                
                # Create conversation
                conversation = Conversation.objects.create(
                    match=match,
                )
                created_conversations += 1
                
                # Add sample messages
                for content, sender_idx in SAMPLE_MESSAGES:
                    sender = user1 if sender_idx == 0 else user2
                    Message.objects.create(
                        conversation=conversation,
                        sender=sender,
                        content=content,
                        message_type="text",
                        is_read=True,
                    )
                
                self.stdout.write(f"  ➕ Created match: {user1_name} <-> {user2_name}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Mock matches seeded: {created_matches} matches, {created_conversations} conversations"
            )
        )
