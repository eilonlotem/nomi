"""
Management command to seed mock users for the application.
This command is idempotent - running it multiple times won't create duplicates.
Usage: python manage.py seed_mock_users

Run on every deploy to ensure mock users exist.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.authtoken.models import Token

from profiles.models import Profile, DisabilityTag, Interest, LookingFor


User = get_user_model()

# Unique identifier prefix for mock users - used to identify and protect them
MOCK_USER_PREFIX = "mock_"

# Mock users data - these are immutable seed users
MOCK_USERS: list[dict[str, Any]] = [
    {
        "username": f"{MOCK_USER_PREFIX}maya",
        "email": "maya@nomi.app",
        "first_name": "Maya",
        "last_name": "Cohen",
        "display_name": "Maya",
        "gender": "female",
        "age": 28,
        "bio": "Wheelchair user who loves adaptive yoga and photography. Looking for genuine connections and someone who appreciates life's simple moments.",
        "tags": ["wheelchairUser", "chronicIllness"],
        "interests": ["Photography", "Yoga", "Art", "Travel", "Coffee"],
        "mood": "open",
        "prompt_id": "laughMost",
        "prompt_answer": "When my cat judges my life choices from across the room",
        "picture_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "casual"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}daniel",
        "email": "daniel@nomi.app",
        "first_name": "Daniel",
        "last_name": "Levy",
        "display_name": "Daniel",
        "gender": "male",
        "age": 32,
        "bio": "Deaf artist and coffee enthusiast. I communicate in sign language and love meeting new people who are patient and curious.",
        "tags": ["deafHoh", "neurodivergent"],
        "interests": ["Art", "Coffee", "Movies", "Cooking", "Gaming"],
        "mood": "chatty",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Gallery hopping in the morning, then sketching at a quiet café",
        "picture_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=500&fit=crop",
        "city": "Jerusalem",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}noa",
        "email": "noa@nomi.app",
        "first_name": "Noa",
        "last_name": "Ben-David",
        "display_name": "Noa",
        "gender": "female",
        "age": 26,
        "bio": "Neurodivergent tech enthusiast. I appreciate patience, understanding, and deep conversations about anything sci-fi.",
        "tags": ["neurodivergent", "autism"],
        "interests": ["Gaming", "Coding", "Sci-Fi", "Music", "Reading"],
        "mood": "lowEnergy",
        "prompt_id": "convinced",
        "prompt_answer": "Robots will eventually appreciate good memes",
        "picture_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=500&fit=crop",
        "city": "Haifa",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["friends", "casual"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}alex",
        "email": "alex@nomi.app",
        "first_name": "Alex",
        "last_name": "Shapiro",
        "display_name": "Alex",
        "gender": "nonbinary",
        "age": 30,
        "bio": "Living with chronic illness. Advocate for disability rights and accessibility. Love nature walks (at my own pace) and meaningful conversations.",
        "tags": ["chronicIllness", "invisible"],
        "interests": ["Writing", "Podcasts", "Nature", "Photography", "Meditation"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "The creative ways I explain my invisible disability to confused strangers",
        "picture_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["male", "female", "nonbinary"],
        "relationship_types": ["serious", "friends"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}sarah",
        "email": "sarah@nomi.app",
        "first_name": "Sarah",
        "last_name": "Miller",
        "display_name": "Sarah",
        "gender": "female",
        "age": 29,
        "bio": "Mental health advocate and proud caregiver. Believer in self-care, genuine connections, and the healing power of a good hike.",
        "tags": ["mentalHealth", "caregiver"],
        "interests": ["Meditation", "Reading", "Hiking", "Cooking", "Yoga"],
        "mood": "open",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Slow morning with coffee, a good book, and an afternoon nature walk",
        "picture_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=500&fit=crop",
        "city": "New York",
        "looking_for_genders": ["male"],
        "relationship_types": ["serious"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}yossi",
        "email": "yossi@nomi.app",
        "first_name": "Yossi",
        "last_name": "Katz",
        "display_name": "Yossi",
        "gender": "male",
        "age": 35,
        "bio": "Mobility difference since childhood. Tech entrepreneur by day, amateur chef by night. Looking for someone who loves good food and better company.",
        "tags": ["mobility", "acquired"],
        "interests": ["Cooking", "Technology", "Travel", "Wine", "Movies"],
        "mood": "chatty",
        "prompt_id": "convinced",
        "prompt_answer": "The best meals are the ones shared with someone special",
        "picture_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["female"],
        "relationship_types": ["serious", "casual"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}emma",
        "email": "emma@nomi.app",
        "first_name": "Emma",
        "last_name": "Wilson",
        "display_name": "Emma",
        "gender": "female",
        "age": 27,
        "bio": "Blind since birth, but I see the world in my own beautiful way. Music lover, podcast addict, and expert hugger.",
        "tags": ["blindLowVision", "cognitive"],
        "interests": ["Music", "Podcasts", "Dancing", "Swimming", "Languages"],
        "mood": "adventurous",
        "prompt_id": "laughMost",
        "prompt_answer": "When people awkwardly wave at me before remembering...",
        "picture_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&h=500&fit=crop",
        "city": "London",
        "looking_for_genders": ["male", "nonbinary"],
        "relationship_types": ["serious", "friends"],
    },
    {
        "username": f"{MOCK_USER_PREFIX}amit",
        "email": "amit@nomi.app",
        "first_name": "Amit",
        "last_name": "Rosen",
        "display_name": "Amit",
        "gender": "male",
        "age": 31,
        "bio": "Autistic and proud. Software developer who speaks fluent sarcasm and Python. Looking for genuine connections, not small talk.",
        "tags": ["autism", "neurodivergent"],
        "interests": ["Coding", "Gaming", "Sci-Fi", "Photography", "Coffee"],
        "mood": "lowEnergy",
        "prompt_id": "perfectSunday",
        "prompt_answer": "Uninterrupted coding session, takeout, and zero social obligations",
        "picture_url": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&h=500&fit=crop",
        "city": "Tel Aviv",
        "looking_for_genders": ["female", "nonbinary"],
        "relationship_types": ["serious"],
    },
]


class Command(BaseCommand):
    help = "Seed immutable mock users for the application (idempotent)"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("🌱 Seeding mock users...")
        
        created = 0
        updated = 0
        
        with transaction.atomic():
            for user_data in MOCK_USERS:
                was_created = self._create_or_update_mock_user(user_data)
                if was_created:
                    created += 1
                else:
                    updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Mock users seeded: {created} created, {updated} updated"
            )
        )
        self.stdout.write(
            f"   Total mock users in database: {User.objects.filter(username__startswith=MOCK_USER_PREFIX).count()}"
        )

    def _create_or_update_mock_user(self, user_data: dict[str, Any]) -> bool:
        """
        Create or update a mock user. Returns True if created, False if updated.
        """
        username = user_data["username"]
        
        # Check if user exists
        user = User.objects.filter(username=username).first()
        was_created = user is None
        
        if was_created:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=user_data["email"],
                password="mockuser123!",  # Mock users can't really login
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )
            self.stdout.write(f"  ➕ Created: {username}")
        else:
            # Update existing user
            user.email = user_data["email"]
            user.first_name = user_data["first_name"]
            user.last_name = user_data["last_name"]
            self.stdout.write(f"  🔄 Updated: {username}")
        
        # Mark as onboarded so they appear in discovery
        user.is_onboarded = True
        user.is_profile_complete = True
        user.is_verified = True
        user.social_provider = "mock"
        user.save()
        
        # Create auth token if doesn't exist
        Token.objects.get_or_create(user=user)
        
        # Create or update profile
        self._create_or_update_profile(user, user_data)
        
        return was_created

    def _create_or_update_profile(self, user: Any, user_data: dict[str, Any]) -> None:
        """Create or update the profile for a mock user."""
        profile, _ = Profile.objects.get_or_create(user=user)
        
        # Update profile fields
        profile.display_name = user_data.get("display_name", user_data["first_name"])
        profile.bio = user_data["bio"]
        profile.current_mood = user_data["mood"]
        profile.gender = user_data["gender"]
        profile.city = user_data.get("city", "Tel Aviv")
        profile.picture_url = user_data.get("picture_url", "")
        profile.prompt_id = user_data.get("prompt_id", "laughMost")
        profile.prompt_answer = user_data.get("prompt_answer", "")
        profile.is_visible = True
        
        # Set age based on data
        age = user_data.get("age", 25)
        profile.date_of_birth = date.today() - timedelta(days=age * 365)
        
        profile.save()
        
        # Clear and re-add tags
        profile.disability_tags.clear()
        for tag_code in user_data.get("tags", []):
            tag = DisabilityTag.objects.filter(code=tag_code).first()
            if tag:
                profile.disability_tags.add(tag)
        
        # Clear and re-add interests
        profile.interests.clear()
        for interest_name in user_data.get("interests", []):
            interest, _ = Interest.objects.get_or_create(
                name=interest_name,
                defaults={"icon": "✨", "category": "Other"}
            )
            profile.interests.add(interest)
        
        # Create or update looking for preferences
        looking_for, _ = LookingFor.objects.get_or_create(
            profile=profile,
            defaults={
                "min_age": 18,
                "max_age": 50,
                "max_distance": 100,
            }
        )
        
        # Update looking for genders
        looking_for.interested_in_men = "male" in user_data.get("looking_for_genders", [])
        looking_for.interested_in_women = "female" in user_data.get("looking_for_genders", [])
        looking_for.interested_in_nonbinary = "nonbinary" in user_data.get("looking_for_genders", [])
        
        # Update relationship types
        rel_types = user_data.get("relationship_types", ["serious"])
        looking_for.looking_for_serious = "serious" in rel_types
        looking_for.looking_for_casual = "casual" in rel_types
        looking_for.looking_for_friends = "friends" in rel_types
        looking_for.looking_for_activity = "activity" in rel_types
        
        looking_for.save()
