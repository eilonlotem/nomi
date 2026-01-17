"""
Custom social auth pipeline functions.
"""
from __future__ import annotations

from typing import Any, Optional

from social_core.backends.base import BaseAuth

from profiles.models import Profile
from users.models import User


def create_user_profile(
    backend: BaseAuth,
    user: User,
    response: dict[str, Any],
    *args: Any,
    **kwargs: Any,
) -> dict[str, Profile]:
    """
    Create a profile for newly registered social users.
    This runs after the user is created/associated.
    """
    # Update user fields from social data
    if backend.name == "facebook":
        # Update user info from Facebook
        if not user.first_name and response.get("first_name"):
            user.first_name = response.get("first_name", "")
        if not user.last_name and response.get("last_name"):
            user.last_name = response.get("last_name", "")
        if not user.email and response.get("email"):
            user.email = response.get("email", "")

        # Mark social provider
        user.social_provider = "facebook"
        user.social_id = response.get("id")
        user.save()

    # Create profile if it doesn't exist
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={
            "display_name": user.first_name or user.username or "User",
        },
    )

    # Update profile photo from Facebook if available
    if created and backend.name == "facebook":
        picture_data: Any = response.get("picture", {})
        if isinstance(picture_data, dict):
            picture_url: Optional[str] = picture_data.get("data", {}).get("url")
            # Note: In production, you'd download and save this image
            # For now, we'll just note that it exists
            _ = picture_url  # Suppress unused variable warning

    return {"profile": profile}
