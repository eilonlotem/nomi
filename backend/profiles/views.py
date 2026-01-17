from __future__ import annotations

from typing import Optional, cast

from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .models import DisabilityTag, Interest, LookingFor, Profile, ProfilePhoto
from .serializers import (
    DisabilityTagSerializer,
    InterestSerializer,
    LookingForSerializer,
    ProfilePhotoSerializer,
    ProfileSerializer,
)


class DisabilityTagListView(generics.ListAPIView):  # type: ignore[type-arg]
    """List all available disability tags."""

    queryset = DisabilityTag.objects.filter(is_active=True)
    serializer_class = DisabilityTagSerializer
    permission_classes = [permissions.AllowAny]


class InterestListView(generics.ListAPIView):  # type: ignore[type-arg]
    """List all available interests."""

    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.AllowAny]


class MyProfileView(generics.RetrieveUpdateAPIView):  # type: ignore[type-arg]
    """Get or update the current user's profile."""

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> Profile:
        user = cast(User, self.request.user)
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={"display_name": user.first_name or "User"},
        )
        return profile


class ProfilePhotoUploadView(APIView):
    """Upload a new profile photo."""

    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        profile: Profile = user.profile

        serializer = ProfilePhotoSerializer(data=request.data)
        if serializer.is_valid():
            # Check photo limit (max 6)
            if profile.photos.count() >= 6:
                return Response(
                    {"error": "Maximum 6 photos allowed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set as primary if first photo
            is_primary: bool = profile.photos.count() == 0

            photo: ProfilePhoto = serializer.save(
                profile=profile,
                is_primary=is_primary,
                order=profile.photos.count(),
            )

            return Response(
                ProfilePhotoSerializer(photo).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, photo_id: int) -> Response:
        user = cast(User, request.user)
        try:
            photo: ProfilePhoto = ProfilePhoto.objects.get(
                id=photo_id,
                profile=user.profile,
            )
            was_primary: bool = photo.is_primary
            photo.delete()

            # If deleted was primary, make first remaining photo primary
            if was_primary:
                first_photo: Optional[ProfilePhoto] = user.profile.photos.first()
                if first_photo:
                    first_photo.is_primary = True
                    first_photo.save()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProfilePhoto.DoesNotExist:
            return Response(
                {"error": "Photo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class SetPrimaryPhotoView(APIView):
    """Set a photo as primary."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, photo_id: int) -> Response:
        user = cast(User, request.user)
        try:
            photo: ProfilePhoto = ProfilePhoto.objects.get(
                id=photo_id,
                profile=user.profile,
            )
            photo.is_primary = True
            photo.save()

            return Response({"success": True})
        except ProfilePhoto.DoesNotExist:
            return Response(
                {"error": "Photo not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UpdateMoodView(APIView):
    """Update current mood."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        mood: Optional[str] = request.data.get("mood")

        valid_moods: list[str] = [choice[0] for choice in Profile.MOOD_CHOICES]
        if mood not in valid_moods:
            return Response(
                {"error": f"Invalid mood. Valid options: {valid_moods}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile: Profile = user.profile
        profile.current_mood = mood or ""
        profile.save()

        return Response({"mood": mood})


class LookingForView(generics.RetrieveUpdateAPIView):  # type: ignore[type-arg]
    """Get or update dating preferences."""

    serializer_class = LookingForSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self) -> LookingFor:
        user = cast(User, self.request.user)
        looking_for, created = LookingFor.objects.get_or_create(profile=user.profile)
        return looking_for
