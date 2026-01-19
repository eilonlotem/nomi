from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, cast

import requests
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import Profile

from .models import Invitation, User
from .serializers import (
    FacebookFriendSerializer,
    InvitationSerializer,
    SendInvitationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserRegistrationView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Register a new user."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: User = serializer.save()

        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class FacebookAuthView(APIView):
    """
    Handle Facebook authentication from frontend.

    Supports two flows:
    1. Access token flow: Frontend sends access_token directly
    2. Authorization code flow: Frontend sends code + redirect_uri
       (used for redirect-based login without popups)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        import os
        
        access_token: Optional[str] = request.data.get("access_token")
        code: Optional[str] = request.data.get("code")
        redirect_uri: Optional[str] = request.data.get("redirect_uri")

        # If authorization code is provided, exchange it for access token
        if code and redirect_uri:
            try:
                app_id = os.environ.get("FACEBOOK_APP_ID", "")
                app_secret = os.environ.get("FACEBOOK_APP_SECRET", "")
                
                if not app_id or not app_secret:
                    return Response(
                        {"error": "Facebook app credentials not configured"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                
                # Exchange code for access token
                token_response = requests.get(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params={
                        "client_id": app_id,
                        "client_secret": app_secret,
                        "redirect_uri": redirect_uri,
                        "code": code,
                    },
                    timeout=10,
                )
                
                if token_response.status_code != 200:
                    error_data = token_response.json()
                    error_msg = error_data.get("error", {}).get("message", "Failed to exchange code")
                    return Response(
                        {"error": f"Facebook token exchange failed: {error_msg}"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                
                token_data = token_response.json()
                access_token = token_data.get("access_token")
                
                if not access_token:
                    return Response(
                        {"error": "No access token in Facebook response"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
                    
            except requests.RequestException as e:
                return Response(
                    {"error": f"Failed to exchange code with Facebook: {str(e)}"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

        if not access_token:
            return Response(
                {"error": "Access token or authorization code is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate token with Facebook Graph API
        try:
            fb_response = requests.get(
                "https://graph.facebook.com/me",
                params={
                    "access_token": access_token,
                    "fields": "id,name,email,first_name,last_name,picture.type(large),birthday,gender",
                },
                timeout=10,
            )

            if fb_response.status_code != 200:
                return Response(
                    {"error": "Invalid Facebook access token"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            fb_data: dict[str, Any] = fb_response.json()

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to verify with Facebook: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Get or create user
        facebook_id: Optional[str] = fb_data.get("id")
        email: str = fb_data.get("email", "")

        # Try to find existing user by social_id or email
        user: Optional[User] = None

        # First, try by Facebook ID
        user = User.objects.filter(
            social_id=facebook_id, social_provider="facebook"
        ).first()

        # If not found and email exists, try by email
        if not user and email:
            user = User.objects.filter(email=email).first()
            if user:
                # Link existing account to Facebook
                user.social_id = facebook_id
                user.social_provider = "facebook"
                user.save()

        # If still not found, create new user
        if not user:
            username: str = f"fb_{facebook_id}"
            user = User.objects.create(
                username=username,
                email=email,
                first_name=fb_data.get("first_name", ""),
                last_name=fb_data.get("last_name", ""),
                social_provider="facebook",
                social_id=facebook_id,
                is_verified=True,  # Facebook verified their email
            )

        # Get profile picture URL
        picture_url: Optional[str] = None
        picture_data: Any = fb_data.get("picture", {})
        if isinstance(picture_data, dict):
            picture_url = picture_data.get("data", {}).get("url")

        # Parse birthday from Facebook (format: MM/DD/YYYY)
        date_of_birth = None
        fb_birthday: Optional[str] = fb_data.get("birthday")
        if fb_birthday:
            try:
                date_of_birth = datetime.strptime(fb_birthday, "%m/%d/%Y").date()
            except ValueError:
                # Try alternate format (just year, or MM/DD)
                try:
                    date_of_birth = datetime.strptime(fb_birthday, "%Y").date()
                except ValueError:
                    pass

        # Map Facebook gender to our choices
        fb_gender: Optional[str] = fb_data.get("gender")
        gender_mapping: dict[str, str] = {
            "male": "male",
            "female": "female",
        }
        gender = gender_mapping.get(fb_gender or "", "")

        # Create profile if it doesn't exist
        profile, profile_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": fb_data.get("first_name")
                or fb_data.get("name")
                or "User",
                "picture_url": picture_url or "",
                "date_of_birth": date_of_birth,
                "gender": gender,
            },
        )

        # Update profile with latest Facebook data if it already exists
        if not profile_created:
            updated = False
            if picture_url and not profile.picture_url:
                profile.picture_url = picture_url
                updated = True
            if date_of_birth and not profile.date_of_birth:
                profile.date_of_birth = date_of_birth
                updated = True
            if gender and not profile.gender:
                profile.gender = gender
                updated = True
            if updated:
                profile.save()

        # Calculate age from date of birth
        age: Optional[int] = None
        if profile.date_of_birth:
            today = datetime.now().date()
            age = (
                today.year
                - profile.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (profile.date_of_birth.month, profile.date_of_birth.day)
                )
            )

        # Get or create auth token
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "token": token.key,
                "is_new_user": profile_created,
                "facebook_data": {
                    "id": facebook_id,
                    "name": fb_data.get("name"),
                    "picture_url": picture_url,
                    "birthday": fb_birthday,
                    "age": age,
                    "gender": fb_gender,
                },
                # Include Facebook access token for features like inviting friends
                "facebook_access_token": access_token,
            }
        )


class SocialAuthView(APIView):
    """
    Generic social authentication handler.
    Routes to appropriate provider handler.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        provider: Optional[str] = request.data.get("provider")
        access_token: Optional[str] = request.data.get("access_token")

        if not provider or not access_token:
            return Response(
                {"error": "Provider and access_token are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if provider == "facebook":
            # Delegate to Facebook handler
            fb_view = FacebookAuthView()
            return fb_view.post(request)

        elif provider == "instagram":
            # Instagram uses Facebook's API (Meta)
            # For Instagram Basic Display API or Instagram Graph API
            return Response(
                {
                    "error": "Instagram authentication not yet implemented. Please use Facebook."
                },
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        else:
            return Response(
                {"error": f"Unknown provider: {provider}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserView(generics.RetrieveUpdateAPIView):  # type: ignore[type-arg]
    """Get or update the current authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> User:
        return cast(User, self.request.user)


class UpdateLanguageView(APIView):
    """Update user's preferred language."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        language: Optional[str] = request.data.get("language")

        valid_languages: list[str] = [choice[0] for choice in User.LANGUAGE_CHOICES]
        if language not in valid_languages:
            return Response(
                {"error": f"Invalid language. Valid options: {valid_languages}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.preferred_language = language
        user.save()

        return Response({"language": language})


class LogoutView(APIView):
    """Logout user by deleting their auth token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        # Delete the user's token
        Token.objects.filter(user=user).delete()

        return Response({"message": "Successfully logged out"})


class ValidateTokenView(APIView):
    """Validate if a token is still valid."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = cast(User, request.user)
        return Response({"valid": True, "user": UserSerializer(user).data})


class CompleteOnboardingView(APIView):
    """Mark user as having completed onboarding."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        user.is_onboarded = True
        user.save()
        return Response({"is_onboarded": True, "user": UserSerializer(user).data})


class FacebookDataDeletionView(APIView):
    """
    Handle Facebook data deletion callback.
    
    Facebook sends a POST request when a user requests data deletion.
    We need to return a confirmation URL and a confirmation code.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        import base64
        import hashlib
        import hmac
        import json
        import os
        from urllib.parse import parse_qs

        signed_request = request.data.get("signed_request", "")
        
        if not signed_request:
            return Response(
                {"error": "Missing signed_request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Parse the signed request
            encoded_sig, payload = signed_request.split(".", 2)
            
            # Decode the payload
            payload += "=" * (4 - len(payload) % 4)  # Add padding
            data = json.loads(base64.urlsafe_b64decode(payload))
            
            user_id = data.get("user_id")
            
            if user_id:
                # Find and delete the user
                username = f"fb_{user_id}"
                user = User.objects.filter(username=username).first()
                
                if user:
                    # Delete user's data
                    from matching.models import Match, Swipe, Message, Conversation
                    from profiles.models import Profile
                    from django.db.models import Q
                    
                    # Delete messages
                    Message.objects.filter(sender=user).delete()
                    
                    # Delete conversations where user is involved
                    matches = Match.objects.filter(Q(user1=user) | Q(user2=user))
                    for match in matches:
                        Conversation.objects.filter(match=match).delete()
                    
                    # Delete matches
                    matches.delete()
                    
                    # Delete swipes
                    Swipe.objects.filter(Q(from_user=user) | Q(to_user=user)).delete()
                    
                    # Delete profile
                    Profile.objects.filter(user=user).delete()
                    
                    # Delete token
                    Token.objects.filter(user=user).delete()
                    
                    # Delete user
                    user.delete()
            
            # Generate confirmation code
            confirmation_code = hashlib.sha256(
                f"{user_id}-{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]
            
            # Return the response Facebook expects
            frontend_url = os.environ.get(
                "FRONTEND_URL", "https://frontend-ylalo.vercel.app"
            )
            
            return Response({
                "url": f"{frontend_url}/data-deletion.html",
                "confirmation_code": confirmation_code,
            })
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FacebookFriendsView(APIView):
    """
    Get Facebook friends who can be invited to the app.
    
    Requires the user_friends permission on Facebook.
    Note: Only returns friends who also use the app (Facebook API limitation).
    For inviting friends who don't use the app, we use the App Invite dialog.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        import os

        user = cast(User, request.user)

        # Get the Facebook access token from the request header or stored token
        access_token: Optional[str] = request.headers.get("X-Facebook-Token")

        if not access_token:
            return Response(
                {"error": "Facebook access token required. Please re-login with Facebook."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Fetch friends from Facebook Graph API
            # Note: This only returns friends who also use this app
            fb_params: dict[str, str] = {
                "access_token": access_token,
                "fields": "id,name,picture.type(large)",
                "limit": "100",
            }
            fb_response = requests.get(
                "https://graph.facebook.com/me/friends",
                params=fb_params,
                timeout=10,
            )

            if fb_response.status_code != 200:
                error_data = fb_response.json()
                error_msg = error_data.get("error", {}).get("message", "Failed to fetch friends")
                return Response(
                    {"error": f"Facebook API error: {error_msg}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            fb_data: dict[str, Any] = fb_response.json()
            friends_data: list[dict[str, Any]] = fb_data.get("data", [])

            # Get list of already-invited friend IDs
            invited_friend_ids = set(
                Invitation.objects.filter(sender=user).values_list(
                    "facebook_friend_id", flat=True
                )
            )

            # Get list of Facebook IDs of users already in the app
            app_user_fb_ids = set(
                User.objects.filter(
                    social_provider="facebook",
                    social_id__isnull=False,
                ).exclude(pk=user.pk).values_list("social_id", flat=True)
            )

            # Format the response
            friends: list[dict[str, Any]] = []
            for friend in friends_data:
                friend_id = friend.get("id", "")
                picture_data = friend.get("picture", {}).get("data", {})
                
                friends.append({
                    "id": friend_id,
                    "name": friend.get("name", ""),
                    "picture_url": picture_data.get("url", ""),
                    "is_app_user": friend_id in app_user_fb_ids,
                    "already_invited": friend_id in invited_friend_ids,
                })

            # Sort: non-invited first, then alphabetically
            friends.sort(key=lambda x: (x["already_invited"], x["name"].lower()))

            return Response({
                "friends": friends,
                "total_count": len(friends),
                "summary": fb_data.get("summary", {}),
            })

        except requests.RequestException as e:
            return Response(
                {"error": f"Failed to fetch Facebook friends: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )


class InvitationsView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """
    List sent invitations or create a new invitation.
    """

    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[no-untyped-def]
        user = cast(User, self.request.user)
        return Invitation.objects.filter(sender=user)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = cast(User, request.user)

        serializer = SendInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        facebook_friend_id: str = serializer.validated_data["facebook_friend_id"]
        facebook_friend_name: str = serializer.validated_data.get(
            "facebook_friend_name", ""
        )

        # Check if already invited
        existing = Invitation.objects.filter(
            sender=user, facebook_friend_id=facebook_friend_id
        ).first()

        if existing:
            return Response(
                InvitationSerializer(existing).data,
                status=status.HTTP_200_OK,
            )

        # Create new invitation
        invitation = Invitation.objects.create(
            sender=user,
            facebook_friend_id=facebook_friend_id,
            facebook_friend_name=facebook_friend_name,
            status="pending",
        )

        return Response(
            InvitationSerializer(invitation).data,
            status=status.HTTP_201_CREATED,
        )


class InvitationStatsView(APIView):
    """
    Get invitation statistics for the current user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = cast(User, request.user)

        total_sent = Invitation.objects.filter(sender=user).count()
        accepted = Invitation.objects.filter(sender=user, status="accepted").count()
        pending = Invitation.objects.filter(sender=user, status="pending").count()

        return Response({
            "total_sent": total_sent,
            "accepted": accepted,
            "pending": pending,
        })
