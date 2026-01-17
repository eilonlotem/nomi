from __future__ import annotations

from typing import Any, Optional, cast

from django.db.models import Q, QuerySet
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import Profile
from profiles.serializers import ProfileCardSerializer
from users.models import User

from .models import Block, Conversation, Match, Message, Swipe
from .serializers import (
    BlockSerializer,
    ConversationSerializer,
    MatchSerializer,
    MessageSerializer,
    SwipeSerializer,
)


class DiscoveryView(APIView):
    """Get profiles for discovery/swiping."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        user = cast(User, request.user)

        # Get blocked users (in either direction)
        blocked_ids_raw: set[tuple[int, int]] = set(
            Block.objects.filter(Q(blocker=user) | Q(blocked=user))
            .values_list("blocker_id", "blocked_id")
            .distinct()
        )
        blocked_ids: set[int] = {id for pair in blocked_ids_raw for id in pair}

        # Get users already swiped on
        swiped_ids: set[int] = set(
            Swipe.objects.filter(from_user=user).values_list("to_user_id", flat=True)
        )

        # Exclude self, blocked, and already swiped
        exclude_ids: set[int] = blocked_ids | swiped_ids | {user.id}

        # Get user's preferences
        min_age: int = 18
        max_age: int = 99
        try:
            looking_for = user.profile.looking_for
            min_age = looking_for.min_age
            max_age = looking_for.max_age
        except Exception:
            pass

        # Query profiles
        profiles: QuerySet[Profile] = (
            Profile.objects.filter(is_visible=True)
            .exclude(user_id__in=exclude_ids)
            .select_related("user")
            .prefetch_related("disability_tags", "interests", "photos")[:20]
        )

        # Calculate compatibility scores
        results: list[dict[str, Any]] = []
        user_tags: set[int] = set()
        if hasattr(user, "profile"):
            user_tags = set(user.profile.disability_tags.values_list("id", flat=True))

        for profile in profiles:
            profile_tags: set[int] = set(
                profile.disability_tags.values_list("id", flat=True)
            )
            shared: set[int] = user_tags & profile_tags

            # Simple compatibility calculation
            compatibility: int = min(100, 50 + len(shared) * 15)

            data: dict[str, Any] = ProfileCardSerializer(profile).data
            data["compatibility"] = compatibility
            data["shared_tags_count"] = len(shared)
            results.append(data)

        return Response(results)


class SwipeView(APIView):
    """Record a swipe action."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        to_user_id: Optional[int] = request.data.get("to_user")
        action: Optional[str] = request.data.get("action")

        if action not in ["pass", "like", "super"]:
            return Response(
                {"error": "Invalid action"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create swipe
        swipe, created = Swipe.objects.get_or_create(
            from_user=user,
            to_user_id=to_user_id,
            defaults={"action": action},
        )

        if not created:
            return Response(
                {"error": "Already swiped on this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for mutual like
        is_match: bool = False
        match: Optional[Match] = None

        if action in ["like", "super"] and to_user_id is not None:
            mutual: bool = Swipe.objects.filter(
                from_user_id=to_user_id,
                to_user=user,
                action__in=["like", "super"],
            ).exists()

            if mutual:
                # Create match
                match = Match.objects.create(
                    user1=user,
                    user2_id=to_user_id,
                )

                # Create conversation for the match
                Conversation.objects.create(match=match)

                is_match = True

        response_data: dict[str, Any] = {
            "swipe": SwipeSerializer(swipe).data,
            "is_match": is_match,
        }

        if is_match and match:
            response_data["match"] = MatchSerializer(
                match, context={"request": request}
            ).data

        return Response(response_data, status=status.HTTP_201_CREATED)


class MatchListView(generics.ListAPIView):  # type: ignore[type-arg]
    """List user's matches."""

    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Match]:
        user = cast(User, self.request.user)
        return Match.objects.filter(
            Q(user1=user) | Q(user2=user),
            is_active=True,
        ).select_related("user1", "user2", "user1__profile", "user2__profile").prefetch_related("conversation")


class ConversationListView(generics.ListAPIView):  # type: ignore[type-arg]
    """List user's conversations."""

    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Conversation]:
        user = cast(User, self.request.user)
        return Conversation.objects.filter(
            Q(match__user1=user) | Q(match__user2=user),
            match__is_active=True,
        ).select_related("match")


class ConversationMessagesView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """Get messages or send a message in a conversation."""

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[Message]:
        conversation_id: int = self.kwargs["conversation_id"]
        return Message.objects.filter(conversation_id=conversation_id).select_related(
            "sender"
        )

    def get_conversation(self) -> Optional[Conversation]:
        user = cast(User, self.request.user)
        conversation_id: int = self.kwargs["conversation_id"]

        return (
            Conversation.objects.filter(id=conversation_id)
            .filter(Q(match__user1=user) | Q(match__user2=user))
            .first()
        )

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = cast(User, request.user)
        conversation: Optional[Conversation] = self.get_conversation()
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Mark messages as read
        conversation.messages.filter(is_read=False).exclude(sender=user).update(
            is_read=True
        )

        return super().list(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        user = cast(User, request.user)
        conversation: Optional[Conversation] = self.get_conversation()
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message: Message = serializer.save(conversation=conversation, sender=user)

        # Update conversation timestamp
        conversation.save()

        return Response(
            MessageSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class BlockUserView(APIView):
    """Block a user."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        serializer = BlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blocked_id: int = serializer.validated_data["blocked"].id

        # Create block
        block, created = Block.objects.get_or_create(
            blocker=user,
            blocked_id=blocked_id,
            defaults={
                "reason": serializer.validated_data.get("reason", ""),
                "description": serializer.validated_data.get("description", ""),
            },
        )

        if not created:
            return Response(
                {"error": "User already blocked"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Deactivate any matches
        Match.objects.filter(
            Q(user1=user, user2_id=blocked_id) | Q(user1_id=blocked_id, user2=user)
        ).update(is_active=False)

        return Response(
            BlockSerializer(block).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request: Request, user_id: int) -> Response:
        user = cast(User, request.user)
        try:
            block: Block = Block.objects.get(blocker=user, blocked_id=user_id)
            block.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Block.DoesNotExist:
            return Response(
                {"error": "Block not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
