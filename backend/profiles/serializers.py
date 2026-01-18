from __future__ import annotations

from datetime import date
from typing import Any, Optional

from rest_framework import serializers

from .models import DisabilityTag, Interest, LookingFor, Profile, ProfilePhoto


class DisabilityTagSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for disability tags."""

    class Meta:
        model = DisabilityTag
        fields: list[str] = [
            "id",
            "code",
            "name_en",
            "name_he",
            "name_es",
            "name_fr",
            "name_ar",
            "icon",
        ]


class InterestSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for interests."""

    class Meta:
        model = Interest
        fields: list[str] = ["id", "name", "icon", "category"]


class ProfilePhotoSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for profile photos."""

    class Meta:
        model = ProfilePhoto
        fields: list[str] = ["id", "image", "url", "is_primary", "order", "uploaded_at"]
        read_only_fields: list[str] = ["id", "uploaded_at"]


class LookingForSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for dating preferences."""

    class Meta:
        model = LookingFor
        fields: list[str] = [
            "genders",
            "relationship_types",
            "min_age",
            "max_age",
            "max_distance",
            "preferred_location",
        ]


class ProfileSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for user profiles."""

    disability_tags = DisabilityTagSerializer(many=True, read_only=True)
    disability_tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DisabilityTag.objects.all(),
        write_only=True,
        source="disability_tags",
    )

    interests = InterestSerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Interest.objects.all(),
        write_only=True,
        source="interests",
    )

    photos = ProfilePhotoSerializer(many=True, read_only=True)
    looking_for = LookingForSerializer(required=False)

    age = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields: list[str] = [
            "id",
            "display_name",
            "bio",
            "date_of_birth",
            "gender",
            "picture_url",
            "city",
            "country",
            "latitude",
            "longitude",
            "disability_tags",
            "disability_tag_ids",
            "interests",
            "interest_ids",
            "current_mood",
            "prompt_id",
            "prompt_answer",
            # Ask Me About It - celebration prompts
            "ask_me_prompt_id",
            "ask_me_answer",
            # Time preferences
            "preferred_times",
            "response_pace",
            "date_pace",
            "time_notes",
            "photos",
            "looking_for",
            "is_visible",
            "show_distance",
            "age",
            "created_at",
            "updated_at",
        ]
        read_only_fields: list[str] = ["id", "created_at", "updated_at", "age"]

    def get_age(self, obj: Profile) -> Optional[int]:
        """Calculate age from date_of_birth."""
        if not obj.date_of_birth:
            return None
        today = date.today()
        return (
            today.year
            - obj.date_of_birth.year
            - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        )

    def create(self, validated_data: dict[str, Any]) -> Profile:
        looking_for_data: Optional[dict[str, Any]] = validated_data.pop(
            "looking_for", None
        )
        disability_tags: list[DisabilityTag] = validated_data.pop("disability_tags", [])
        interests: list[Interest] = validated_data.pop("interests", [])

        profile: Profile = Profile.objects.create(**validated_data)
        profile.disability_tags.set(disability_tags)
        profile.interests.set(interests)

        if looking_for_data:
            LookingFor.objects.create(profile=profile, **looking_for_data)

        return profile

    def update(self, instance: Profile, validated_data: dict[str, Any]) -> Profile:
        looking_for_data: Optional[dict[str, Any]] = validated_data.pop(
            "looking_for", None
        )
        disability_tags: Optional[list[DisabilityTag]] = validated_data.pop(
            "disability_tags", None
        )
        interests: Optional[list[Interest]] = validated_data.pop("interests", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if disability_tags is not None:
            instance.disability_tags.set(disability_tags)

        if interests is not None:
            instance.interests.set(interests)

        if looking_for_data:
            LookingFor.objects.update_or_create(
                profile=instance,
                defaults=looking_for_data,
            )

        return instance


class ProfileCardSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """
    Minimal profile serializer for discovery cards.
    Excludes sensitive/unnecessary data.
    """

    disability_tags = DisabilityTagSerializer(many=True, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    photos = ProfilePhotoSerializer(many=True, read_only=True)
    primary_photo = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Profile
        fields: list[str] = [
            "id",
            "user_id",
            "display_name",
            "bio",
            "city",
            "gender",
            "picture_url",
            "disability_tags",
            "interests",
            "current_mood",
            "prompt_id",
            "prompt_answer",
            # Ask Me About It - celebration prompts
            "ask_me_prompt_id",
            "ask_me_answer",
            # Time preferences
            "preferred_times",
            "response_pace",
            "date_pace",
            "photos",
            "primary_photo",
            "age",
        ]

    def get_primary_photo(self, obj: Profile) -> Optional[dict[str, Any]]:
        """Get primary photo, or use picture_url as fallback."""
        photo: Optional[ProfilePhoto] = obj.photos.filter(is_primary=True).first()
        if photo:
            return dict(ProfilePhotoSerializer(photo).data)
        # Fallback to picture_url from social login
        if obj.picture_url:
            return {"url": obj.picture_url, "is_primary": True}
        return None

    def get_age(self, obj: Profile) -> Optional[int]:
        """Calculate age from date_of_birth."""
        if not obj.date_of_birth:
            return None
        today = date.today()
        return (
            today.year
            - obj.date_of_birth.year
            - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
        )
