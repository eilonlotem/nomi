from __future__ import annotations

from typing import Any

from rest_framework import serializers

from .models import Invitation, User


class UserSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for User model."""

    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields: list[str] = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "social_provider",
            "date_of_birth",
            "age",
            "preferred_language",
            "is_verified",
            "is_profile_complete",
            "is_onboarded",
            "last_active",
            "created_at",
        ]
        read_only_fields: list[str] = [
            "id",
            "social_provider",
            "is_verified",
            "created_at",
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for user registration."""

    class Meta:
        model = User
        fields: list[str] = ["email", "username", "password", "first_name", "last_name"]
        extra_kwargs: dict[str, dict[str, bool]] = {"password": {"write_only": True}}

    def create(self, validated_data: dict[str, Any]) -> User:
        user: User = User.objects.create_user(**validated_data)
        return user


class SocialAuthSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for social authentication."""

    provider = serializers.ChoiceField(choices=["facebook", "instagram"])
    access_token = serializers.CharField()

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        # In a real app, validate the access token with the provider
        return data


class FacebookFriendSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for Facebook friend data."""

    id = serializers.CharField()
    name = serializers.CharField()
    picture_url = serializers.CharField(required=False, allow_blank=True)
    is_app_user = serializers.BooleanField(default=False)
    already_invited = serializers.BooleanField(default=False)


class InvitationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for Invitation model."""

    sender_name = serializers.CharField(source="sender.first_name", read_only=True)

    class Meta:
        model = Invitation
        fields: list[str] = [
            "id",
            "sender",
            "sender_name",
            "facebook_friend_id",
            "facebook_friend_name",
            "invited_user",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields: list[str] = [
            "id",
            "sender",
            "sender_name",
            "invited_user",
            "status",
            "created_at",
            "updated_at",
        ]


class SendInvitationSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for sending an invitation."""

    facebook_friend_id = serializers.CharField()
    facebook_friend_name = serializers.CharField(required=False, allow_blank=True)
