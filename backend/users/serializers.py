from __future__ import annotations

from typing import Any

from rest_framework import serializers

from .models import User


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
