from __future__ import annotations

from typing import Any, Optional

from rest_framework import serializers

from profiles.serializers import ProfileCardSerializer
from users.models import User
from users.serializers import UserSerializer

from .models import Block, Conversation, Match, Message, Swipe


class SwipeSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for swipe actions."""

    class Meta:
        model = Swipe
        fields: list[str] = ["id", "to_user", "action", "created_at"]
        read_only_fields: list[str] = ["id", "created_at"]


class MatchSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for matches."""

    other_user = serializers.SerializerMethodField()
    other_profile = serializers.SerializerMethodField()
    conversation_id = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields: list[str] = [
            "id",
            "other_user",
            "other_profile",
            "conversation_id",
            "matched_at",
            "compatibility_score",
            "shared_tags_count",
            "shared_interests_count",
            "compatibility_breakdown",
            "is_active",
        ]

    def get_other_user(self, obj: Match) -> dict[str, Any]:
        request_user: User = self.context["request"].user
        other: User = obj.user2 if obj.user1 == request_user else obj.user1
        return dict(UserSerializer(other).data)

    def get_other_profile(self, obj: Match) -> Optional[dict[str, Any]]:
        request_user: User = self.context["request"].user
        other: User = obj.user2 if obj.user1 == request_user else obj.user1
        if hasattr(other, "profile"):
            return dict(ProfileCardSerializer(other.profile).data)
        return None

    def get_conversation_id(self, obj: Match) -> Optional[int]:
        if hasattr(obj, "conversation"):
            return obj.conversation.id
        return None


class MessageSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for chat messages."""

    sender_name = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields: list[str] = [
            "id",
            "sender",
            "sender_name",
            "is_mine",
            "message_type",
            "content",
            "audio_url",
            "audio_duration",
            "is_read",
            "read_at",
            "sent_at",
        ]
        read_only_fields: list[str] = ["id", "sender", "is_read", "read_at", "sent_at"]

    def get_sender_name(self, obj: Message) -> str:
        try:
            if hasattr(obj.sender, "profile") and obj.sender.profile:
                return obj.sender.profile.display_name or obj.sender.username
        except Exception:
            pass
        return obj.sender.username if obj.sender else "Unknown"

    def get_is_mine(self, obj: Message) -> bool:
        request = self.context.get("request")
        if request:
            return bool(obj.sender == request.user)
        return False


class VoiceMessageSerializer(serializers.Serializer):  # type: ignore[type-arg]
    """Serializer for voice message upload."""

    audio = serializers.FileField(required=True)
    duration = serializers.IntegerField(required=False, default=0)

    def validate_audio(self, value: Any) -> Any:
        """Validate audio file."""
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("Audio file too large. Maximum size is 10MB.")

        # Check content type
        allowed_types = [
            "audio/webm",
            "audio/ogg",
            "audio/mp4",
            "audio/mpeg",
            "audio/wav",
            "audio/mp3",
            "audio/m4a",
            "audio/x-m4a",
        ]
        content_type = getattr(value, "content_type", "")
        if content_type and content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Unsupported audio format: {content_type}. Allowed: webm, ogg, mp4, mpeg, wav"
            )

        return value


class ConversationSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for conversations."""

    match = MatchSerializer(read_only=True)
    last_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields: list[str] = [
            "id",
            "match",
            "last_message",
            "unread_count",
            "created_at",
            "updated_at",
        ]

    def get_unread_count(self, obj: Conversation) -> int:
        request = self.context.get("request")
        if request:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class BlockSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for block reports."""

    class Meta:
        model = Block
        fields: list[str] = ["id", "blocked", "reason", "description", "created_at"]
        read_only_fields: list[str] = ["id", "created_at"]
