"""
Management command to create matches for a specific user with mock users.
Usage: python manage.py create_user_matches <email_or_username>
"""
from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from matching.models import Swipe, Match, Conversation, Message


User = get_user_model()

MOCK_USER_PREFIX = "mock_"

SAMPLE_MESSAGES = [
    ("Hey! I saw your profile and thought we might have a lot in common 😊", 1),
    ("Hi! Thanks for reaching out. What caught your attention?", 0),
    ("I love that you're into photography! I've been trying to get into it myself.", 1),
    ("That's awesome! Feel free to ask me anything about it. What kind of photos do you like?", 0),
]


class Command(BaseCommand):
    help = "Create matches for a specific user with mock users"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "identifier",
            type=str,
            help="Email or username of the user to create matches for",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=3,
            help="Number of mock users to match with (default: 3)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        identifier = options["identifier"]
        count = options["count"]
        
        # Find the user
        user = User.objects.filter(
            Q(email=identifier) | Q(username=identifier)
        ).first()
        
        if not user:
            self.stdout.write(self.style.ERROR(f"User not found: {identifier}"))
            self.stdout.write("Available users:")
            for u in User.objects.all()[:20]:
                self.stdout.write(f"  - {u.username} ({u.email})")
            return
        
        self.stdout.write(f"💕 Creating matches for: {user.username} ({user.email})")
        
        # Get mock users
        mock_users = User.objects.filter(
            username__startswith=MOCK_USER_PREFIX
        ).exclude(id=user.id)[:count]
        
        if not mock_users:
            self.stdout.write(self.style.ERROR("No mock users found. Run seed_mock_users first."))
            return
        
        created_matches = 0
        
        with transaction.atomic():
            for mock_user in mock_users:
                # Check if match already exists
                existing_match = Match.objects.filter(
                    Q(user1=user, user2=mock_user) | Q(user1=mock_user, user2=user)
                ).first()
                
                if existing_match:
                    self.stdout.write(f"  🔄 Match already exists: {mock_user.username}")
                    continue
                
                # Create mutual swipes
                Swipe.objects.get_or_create(
                    from_user=user,
                    to_user=mock_user,
                    defaults={"action": "like"}
                )
                Swipe.objects.get_or_create(
                    from_user=mock_user,
                    to_user=user,
                    defaults={"action": "like"}
                )
                
                # Create match
                match = Match.objects.create(
                    user1=user,
                    user2=mock_user,
                    compatibility_score=80,
                    shared_tags_count=2,
                )
                
                # Create conversation
                conversation = Conversation.objects.create(match=match)
                
                # Add sample messages
                for content, sender_idx in SAMPLE_MESSAGES:
                    sender = user if sender_idx == 0 else mock_user
                    Message.objects.create(
                        conversation=conversation,
                        sender=sender,
                        content=content,
                        message_type="text",
                        is_read=True,
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f"  ➕ Created match: {user.username} <-> {mock_user.username}")
                )
                created_matches += 1
        
        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Created {created_matches} matches for {user.username}")
        )
