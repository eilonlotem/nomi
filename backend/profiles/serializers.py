from __future__ import annotations

from datetime import date
from typing import Any, Optional

from rest_framework import serializers

from users.models import User

from .models import (
    DisabilityTag,
    Interest,
    LookingFor,
    Profile,
    ProfileDisabilityTagVisibility,
    ProfilePhoto,
)


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
            "category",
            "disclosure_level",
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
            "min_age",
            "max_age",
            "max_distance",
            "preferred_location",
        ]


class ProfileTagVisibilitySerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for profile tag visibility settings."""

    tag = DisabilityTagSerializer(read_only=True)
    tag_id = serializers.PrimaryKeyRelatedField(
        queryset=DisabilityTag.objects.all(),
        write_only=True,
        source="tag",
    )
    allowed_viewer_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        source="allowed_viewers",
    )

    class Meta:
        model = ProfileDisabilityTagVisibility
        fields: list[str] = [
            "id",
            "tag",
            "tag_id",
            "visibility",
            "allowed_viewer_ids",
        ]


class ProfileSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for user profiles."""

    disability_tags = serializers.SerializerMethodField()
    disability_tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DisabilityTag.objects.all(),
        write_only=True,
        source="disability_tags",
    )
    disability_tag_visibilities = ProfileTagVisibilitySerializer(
        many=True, required=False, source="tag_visibilities"
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
            "disability_tag_visibilities",
            "interests",
            "interest_ids",
            "prompt_id",
            "prompt_answer",
            # Time preferences
            "preferred_times",
            "response_pace",
            "date_pace",
            "time_notes",
            # Relationship intent and openness
            "relationship_intent",
            "openness_tags",
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

    def get_disability_tags(self, obj: Profile) -> list[dict[str, Any]]:
        """Return all disability tags for the profile owner."""
        tags = obj.disability_tags.all()
        return list(DisabilityTagSerializer(tags, many=True).data)

    def _apply_tag_visibilities(
        self,
        profile: Profile,
        visibility_data: list[dict[str, Any]],
    ) -> None:
        updated_tag_ids: set[int] = set()
        for entry in visibility_data:
            tag: Optional[DisabilityTag] = entry.get("tag")
            if not tag:
                continue
            visibility = entry.get("visibility", "public")
            allowed_viewers = entry.get("allowed_viewers", [])

            record, _ = ProfileDisabilityTagVisibility.objects.update_or_create(
                profile=profile,
                tag=tag,
                defaults={"visibility": visibility},
            )
            if allowed_viewers is not None:
                record.allowed_viewers.set(allowed_viewers)
            updated_tag_ids.add(tag.id)

        if visibility_data:
            ProfileDisabilityTagVisibility.objects.filter(profile=profile).exclude(
                tag_id__in=updated_tag_ids
            ).delete()
        else:
            ProfileDisabilityTagVisibility.objects.filter(profile=profile).delete()

    def create(self, validated_data: dict[str, Any]) -> Profile:
        looking_for_data: Optional[dict[str, Any]] = validated_data.pop(
            "looking_for", None
        )
        disability_tags: list[DisabilityTag] = validated_data.pop("disability_tags", [])
        disability_tag_visibilities: list[dict[str, Any]] = validated_data.pop(
            "tag_visibilities", []
        )
        interests: list[Interest] = validated_data.pop("interests", [])

        profile: Profile = Profile.objects.create(**validated_data)
        profile.disability_tags.set(disability_tags)
        profile.interests.set(interests)

        if disability_tag_visibilities:
            self._apply_tag_visibilities(profile, disability_tag_visibilities)

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
        disability_tag_visibilities: Optional[list[dict[str, Any]]] = validated_data.pop(
            "tag_visibilities", None
        )
        interests: Optional[list[Interest]] = validated_data.pop("interests", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if disability_tag_visibilities is not None and disability_tags is None:
            disability_tags = [entry.get("tag") for entry in disability_tag_visibilities if entry.get("tag")]

        if disability_tags is not None:
            instance.disability_tags.set(disability_tags)

        if disability_tag_visibilities is not None:
            self._apply_tag_visibilities(instance, disability_tag_visibilities)

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
    is_bot = serializers.SerializerMethodField()

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
            "prompt_id",
            "prompt_answer",
            "relationship_intent",
            "openness_tags",
            # Time preferences
            "preferred_times",
            "response_pace",
            "date_pace",
            "photos",
            "primary_photo",
            "age",
            "is_bot",
        ]

    def get_disability_tags(self, obj: Profile) -> list[dict[str, Any]]:
        request = self.context.get("request")
        viewer: Optional[User] = None
        if request and hasattr(request, "user") and request.user.is_authenticated:
            viewer = request.user

        tags = list(obj.disability_tags.all())
        if not viewer or viewer == obj.user:
            return list(DisabilityTagSerializer(tags, many=True).data)

        visibility_records = list(obj.tag_visibilities.all().prefetch_related("allowed_viewers"))
        visibility_by_tag = {record.tag_id: record for record in visibility_records}
        allowed_by_tag = {
            record.tag_id: set(record.allowed_viewers.values_list("id", flat=True))
            for record in visibility_records
        }

        try:
            from matching.models import Match

            is_match = Match.get_match_between(viewer, obj.user) is not None
        except Exception:
            is_match = False

        visible_tags: list[DisabilityTag] = []
        for tag in tags:
            record = visibility_by_tag.get(tag.id)
            if record is None or record.visibility == "public":
                visible_tags.append(tag)
                continue
            if record.visibility == "matches" and is_match:
                visible_tags.append(tag)
                continue
            if record.visibility == "specific":
                if viewer.id in allowed_by_tag.get(tag.id, set()):
                    visible_tags.append(tag)

        return list(DisabilityTagSerializer(visible_tags, many=True).data)

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

    def get_is_bot(self, obj: Profile) -> bool:
        """Return True if this is a mock/bot user."""
        return obj.user.social_provider == "mock"
