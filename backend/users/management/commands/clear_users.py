"""
Management command to clear all users and related data from the database.
Usage: python manage.py clear_users
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from profiles.models import Profile, ProfilePhoto, LookingFor
from matching.models import Swipe, Match, Conversation, Message, Block


User = get_user_model()


class Command(BaseCommand):
    help = 'Clear all users and related data from the database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--keep-superusers',
            action='store_true',
            help='Keep superuser accounts',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args: object, **options: object) -> None:
        keep_superusers = options.get('keep_superusers', False)
        confirm = options.get('confirm', False)

        # Count what will be deleted
        if keep_superusers:
            users_to_delete = User.objects.filter(is_superuser=False)
        else:
            users_to_delete = User.objects.all()

        user_count = users_to_delete.count()
        token_count = Token.objects.count()
        profile_count = Profile.objects.count()
        photo_count = ProfilePhoto.objects.count()
        looking_for_count = LookingFor.objects.count()
        swipe_count = Swipe.objects.count()
        match_count = Match.objects.count()
        conversation_count = Conversation.objects.count()
        message_count = Message.objects.count()
        block_count = Block.objects.count()

        self.stdout.write(self.style.WARNING(
            f'\nThis will delete:'
            f'\n  - {user_count} users'
            f'\n  - {token_count} auth tokens'
            f'\n  - {profile_count} profiles'
            f'\n  - {photo_count} profile photos'
            f'\n  - {looking_for_count} looking for preferences'
            f'\n  - {swipe_count} swipes'
            f'\n  - {match_count} matches'
            f'\n  - {conversation_count} conversations'
            f'\n  - {message_count} messages'
            f'\n  - {block_count} blocks'
        ))

        if keep_superusers:
            superuser_count = User.objects.filter(is_superuser=True).count()
            self.stdout.write(self.style.NOTICE(
                f'\n  (Keeping {superuser_count} superuser accounts)'
            ))

        if not confirm:
            response = input('\nAre you sure you want to proceed? [y/N] ')
            if response.lower() != 'y':
                self.stdout.write(self.style.ERROR('Aborted.'))
                return

        # Delete in order (to respect foreign keys)
        self.stdout.write('Deleting messages...')
        Message.objects.all().delete()

        self.stdout.write('Deleting conversations...')
        Conversation.objects.all().delete()

        self.stdout.write('Deleting matches...')
        Match.objects.all().delete()

        self.stdout.write('Deleting swipes...')
        Swipe.objects.all().delete()

        self.stdout.write('Deleting blocks...')
        Block.objects.all().delete()

        self.stdout.write('Deleting looking for preferences...')
        LookingFor.objects.all().delete()

        self.stdout.write('Deleting profile photos...')
        ProfilePhoto.objects.all().delete()

        self.stdout.write('Deleting profiles...')
        Profile.objects.all().delete()

        self.stdout.write('Deleting auth tokens...')
        Token.objects.all().delete()

        self.stdout.write('Deleting users...')
        users_to_delete.delete()

        self.stdout.write(self.style.SUCCESS('\n✅ Database cleaned successfully!'))
