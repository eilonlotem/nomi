"""
Management command to completely reset the database and reseed with initial data.
Usage: python manage.py reset_db
"""
from __future__ import annotations

from django.core.management.base import BaseCommand, CommandParser
from django.core.management import call_command
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = 'Reset the database: clear all data and reseed with initial data'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )
        parser.add_argument(
            '--create-superuser',
            action='store_true',
            help='Create a default superuser (admin/admin)',
        )

    def handle(self, *args: object, **options: object) -> None:
        confirm = options.get('confirm', False)
        create_superuser = options.get('create_superuser', False)

        if not confirm:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  This will DELETE ALL DATA and reset the database!'
            ))
            response = input('\nAre you sure you want to proceed? [y/N] ')
            if response.lower() != 'y':
                self.stdout.write(self.style.ERROR('Aborted.'))
                return

        # Step 1: Clear all users
        self.stdout.write(self.style.NOTICE('\n📦 Step 1: Clearing database...'))
        call_command('clear_users', confirm=True)

        # Step 2: Reseed initial data
        self.stdout.write(self.style.NOTICE('\n🌱 Step 2: Seeding initial data...'))
        call_command('seed_data')

        # Step 3: Optionally create superuser
        if create_superuser:
            self.stdout.write(self.style.NOTICE('\n👤 Step 3: Creating superuser...'))
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin',
                    first_name='Admin',
                    last_name='User',
                )
                self.stdout.write(self.style.SUCCESS(
                    '  Created superuser: admin / admin'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    '  Superuser "admin" already exists'
                ))

        self.stdout.write(self.style.SUCCESS('\n✅ Database reset complete!'))
