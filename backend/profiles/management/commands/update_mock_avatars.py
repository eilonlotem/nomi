"""
Update existing mock users with locally generated avatars.

Usage:
  python manage.py update_mock_avatars
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from profiles.models import Profile, ProfilePhoto
from profiles.management.commands.seed_mock_users import MOCK_USERS, MOCK_USER_PREFIX


User = get_user_model()


def get_local_avatar_url(username: str) -> str | None:
    """
    Get the URL for a locally generated avatar if it exists.
    Always returns absolute URL when BACKEND_URL is set, otherwise relative URL.
    """
    avatar_path = Path(settings.BASE_DIR) / "static" / "painted_avatars" / username / "avatar_1.png"
    if avatar_path.exists():
        backend_url = os.getenv("BACKEND_URL", "").rstrip("/")
        if backend_url:
            # Return absolute URL
            return f"{backend_url}/static/painted_avatars/{username}/avatar_1.png"
        # For local development, return relative URL
        # Frontend will prepend the backend URL from API_URL env var
        return f"/static/painted_avatars/{username}/avatar_1.png"
    return None


class Command(BaseCommand):
    help = "Update existing mock users with locally generated avatars"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without making changes",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run = options.get("dry_run", False)
        
        self.stdout.write("🖼️  Updating mock user avatars...")
        
        updated = 0
        skipped = 0
        
        for user_data in MOCK_USERS:
            username = user_data["username"]
            
            # Check if local avatar exists
            local_avatar = get_local_avatar_url(username)
            if not local_avatar:
                self.stdout.write(f"   ⏭️  {username}: No local avatar found")
                skipped += 1
                continue
            
            # Find the user
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(f"   ⏭️  {username}: User not found")
                skipped += 1
                continue
            
            if not hasattr(user, "profile"):
                self.stdout.write(f"   ⏭️  {username}: No profile")
                skipped += 1
                continue
            
            profile = user.profile
            
            if dry_run:
                self.stdout.write(f"   📷 {username}: Would update to {local_avatar}")
                updated += 1
                continue
            
            # Update profile picture_url
            profile.picture_url = local_avatar
            profile.save(update_fields=["picture_url"])
            
            # Update or create primary ProfilePhoto
            primary_photo = profile.photos.filter(is_primary=True).first()
            if primary_photo:
                primary_photo.url = local_avatar
                primary_photo.save(update_fields=["url"])
            else:
                ProfilePhoto.objects.create(
                    profile=profile,
                    url=local_avatar,
                    is_primary=True,
                    order=0,
                )
            
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ {username}: Updated to local avatar")
            )
            updated += 1
        
        if dry_run:
            self.stdout.write(f"\n🔍 Dry run: {updated} would be updated, {skipped} skipped")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Done! {updated} updated, {skipped} skipped")
            )
