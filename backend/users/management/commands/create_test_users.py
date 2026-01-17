"""
Management command to create test users for development.
Usage: python manage.py create_test_users
"""
from __future__ import annotations

import random
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from profiles.models import Profile, DisabilityTag, Interest, LookingFor


User = get_user_model()


# Sample data for test users
TEST_USERS = [
    {
        'username': 'maya_test',
        'email': 'maya@test.com',
        'first_name': 'Maya',
        'last_name': 'Cohen',
        'display_name': 'Maya',
        'gender': 'female',
        'age': 28,
        'bio': 'Wheelchair user who loves adaptive yoga and photography. Looking for genuine connections.',
        'tags': ['wheelchairUser', 'chronicIllness'],
        'interests': ['Photography', 'Yoga', 'Art', 'Travel'],
        'mood': 'open',
        'prompt_id': 'laughMost',
        'prompt_answer': 'When my cat judges my life choices',
        'picture_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=500&fit=crop',
    },
    {
        'username': 'daniel_test',
        'email': 'daniel@test.com',
        'first_name': 'Daniel',
        'last_name': 'Levy',
        'display_name': 'Daniel',
        'gender': 'male',
        'age': 32,
        'bio': 'Deaf artist and coffee enthusiast. I communicate in sign language.',
        'tags': ['deafHoh', 'neurodivergent'],
        'interests': ['Art', 'Coffee', 'Sign Language', 'Movies'],
        'mood': 'chatty',
        'prompt_id': 'perfectSunday',
        'prompt_answer': 'Gallery hopping, then sketching at a quiet café',
        'picture_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop',
    },
    {
        'username': 'noa_test',
        'email': 'noa@test.com',
        'first_name': 'Noa',
        'last_name': 'Ben-David',
        'display_name': 'Noa',
        'gender': 'female',
        'age': 26,
        'bio': 'Neurodivergent tech enthusiast. I appreciate patience and understanding.',
        'tags': ['neurodivergent', 'autism'],
        'interests': ['Gaming', 'Coding', 'Sci-Fi', 'Music'],
        'mood': 'lowEnergy',
        'prompt_id': 'convinced',
        'prompt_answer': 'Robots will eventually appreciate good memes',
        'picture_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop',
    },
    {
        'username': 'alex_test',
        'email': 'alex@test.com',
        'first_name': 'Alex',
        'last_name': 'Shapiro',
        'display_name': 'Alex',
        'gender': 'nonbinary',
        'age': 30,
        'bio': 'Living with chronic illness. Advocate for disability rights and accessibility.',
        'tags': ['chronicIllness', 'invisible'],
        'interests': ['Writing', 'Activism', 'Podcasts', 'Nature'],
        'mood': 'adventurous',
        'prompt_id': 'laughMost',
        'prompt_answer': 'Explaining my invisible disability to confused strangers',
        'picture_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop',
    },
    {
        'username': 'sarah_test',
        'email': 'sarah@test.com',
        'first_name': 'Sarah',
        'last_name': 'Miller',
        'display_name': 'Sarah',
        'gender': 'female',
        'age': 29,
        'bio': 'Mental health advocate. Believer in self-care and genuine connections.',
        'tags': ['mentalHealth', 'caregiver'],
        'interests': ['Meditation', 'Reading', 'Hiking', 'Cooking'],
        'mood': 'open',
        'prompt_id': 'perfectSunday',
        'prompt_answer': 'Slow morning with coffee, a good book, and a nature walk',
        'picture_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop',
    },
]


class Command(BaseCommand):
    help = 'Create test users for development'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of test users to create (default: 5)',
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing test users before creating new ones',
        )

    def handle(self, *args: object, **options: object) -> None:
        count = min(options.get('count', 5), len(TEST_USERS))
        clear_existing = options.get('clear_existing', False)

        if clear_existing:
            self.stdout.write('Clearing existing test users...')
            test_usernames = [u['username'] for u in TEST_USERS]
            User.objects.filter(username__in=test_usernames).delete()

        created_count = 0
        for user_data in TEST_USERS[:count]:
            username = user_data['username']

            if User.objects.filter(username=username).exists():
                self.stdout.write(f'  User {username} already exists, skipping...')
                continue

            # Create user
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password='testpass123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )
            # Mark as onboarded so they appear in discovery
            user.is_onboarded = True
            user.is_profile_complete = True
            user.save()

            # Create auth token
            Token.objects.create(user=user)

            # Create or get profile with complete data
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.display_name = user_data.get('display_name', user_data['first_name'])
            profile.bio = user_data['bio']
            profile.current_mood = user_data['mood']
            profile.gender = user_data['gender']
            profile.city = random.choice(['Tel Aviv', 'Jerusalem', 'Haifa', 'New York', 'London'])
            profile.picture_url = user_data.get('picture_url', '')
            profile.prompt_id = user_data.get('prompt_id', 'laughMost')
            profile.prompt_answer = user_data.get('prompt_answer', '')
            
            # Set age based on data (create a date of birth)
            from datetime import date, timedelta
            age = user_data.get('age', 25)
            profile.date_of_birth = date.today() - timedelta(days=age * 365)
            
            profile.is_visible = True
            profile.save()

            # Add tags
            for tag_code in user_data['tags']:
                tag = DisabilityTag.objects.filter(code=tag_code).first()
                if tag:
                    profile.disability_tags.add(tag)

            # Add interests
            for interest_name in user_data['interests']:
                interest, _ = Interest.objects.get_or_create(name=interest_name)
                profile.interests.add(interest)

            # Create looking for preferences
            LookingFor.objects.get_or_create(
                profile=profile,
                defaults={
                    'min_age': 18,
                    'max_age': 45,
                    'max_distance': 50,
                }
            )

            self.stdout.write(self.style.SUCCESS(
                f'  ✅ Created user: {username} (password: testpass123)'
            ))
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Created {created_count} test users!'
        ))
        self.stdout.write(self.style.NOTICE(
            '\nTest user credentials:'
            '\n  Password for all: testpass123'
            '\n  Usernames: ' + ', '.join([u['username'] for u in TEST_USERS[:count]])
        ))
