from __future__ import annotations

import logging
from typing import Any, Iterable, Optional, cast

from django.core.cache import cache
from django.db.models import Q, QuerySet
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import Profile
from profiles.serializers import ProfileCardSerializer
from users.models import User

from .algorithm import ProfileRanker
from .ai_service import generate_conversation_summary, generate_message_suggestions
from .models import Block, Conversation, Match, Message, ShortcutResponse, Swipe
from .serializers import (
    BlockSerializer,
    ConversationSerializer,
    MatchSerializer,
    MessageSerializer,
    ShortcutSerializer,
    SwipeSerializer,
    VoiceMessageSerializer,
)

logger = logging.getLogger(__name__)


def _get_conversation_for_user(
    user: User, conversation_id: int
) -> Optional[Conversation]:
    return (
        Conversation.objects.filter(id=conversation_id)
        .filter(Q(match__user1=user) | Q(match__user2=user))
        .select_related(
            "match",
            "match__user1",
            "match__user2",
            "match__user1__profile",
            "match__user2__profile",
        )
        .first()
    )


def _build_conversation_history(
    messages: Iterable[Message], user: User
) -> list[dict[str, str]]:
    history: list[dict[str, str]] = []
    for msg in messages:
        role = "user" if msg.sender_id == user.id else "assistant"
        content = msg.content or ""
        if msg.message_type == "voice":
            content = "[Voice message]"
        history.append({"role": role, "content": content})
    return history


def _get_request_language(request: Request) -> str:
    language = request.query_params.get("lang")
    if not language:
        accept_language = request.headers.get("Accept-Language", "")
        language = accept_language.split(",")[0].split("-")[0].strip()
    if language not in {"en", "he", "es", "fr", "ar"}:
        return "en"
    return language


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

        # Exclude the support avatar from discovery
        from .support import SUPPORT_USERNAME
        support_ids: set[int] = set(
            User.objects.filter(username=SUPPORT_USERNAME).values_list("id", flat=True)
        )

        # Exclude self, blocked, already swiped, and support user
        exclude_ids: set[int] = blocked_ids | swiped_ids | support_ids | {user.id}

        # Query candidate profiles with prefetched data for algorithm
        candidates: QuerySet[Profile] = (
            Profile.objects.filter(is_visible=True)
            .exclude(user_id__in=exclude_ids)
            .select_related("user", "looking_for")
            .prefetch_related(
                "disability_tags",
                "interests",
                "photos",
                "tag_visibilities",
                "tag_visibilities__allowed_viewers",
            )
        )

        # Ensure user's profile has looking_for loaded for filtering
        # This is critical for the matching algorithm
        if hasattr(user, "profile"):
            # Force load the looking_for relationship
            try:
                _ = user.profile.looking_for
            except Exception:
                pass  # User may not have looking_for preferences set
        
        # Use the matching algorithm to filter and rank profiles
        # Only show relevant people based on preferences
        ranker = ProfileRanker()
        ranked_profiles = ranker.get_ranked_profiles(
            user=user,
            candidates=candidates,
            limit=20,
            min_score=35,  # Only show reasonably compatible matches
            filter_irrelevant=True,  # Filter out mismatched gender/age/distance
        )

        # Build response with compatibility data
        results: list[dict[str, Any]] = []
        for profile, breakdown in ranked_profiles:
            data: dict[str, Any] = ProfileCardSerializer(
                profile, context={"request": request}
            ).data
            data["compatibility"] = breakdown.total_score
            data["shared_tags_count"] = breakdown.shared_tags_count
            data["shared_interests_count"] = breakdown.shared_interests_count
            data["compatibility_breakdown"] = breakdown.to_dict()
            results.append(data)

        return Response(results)


class SwipeView(APIView):
    """Record a swipe action."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        to_user_id: Optional[int] = request.data.get("to_user")
        action: Optional[str] = request.data.get("action")

        if action not in ["pass", "like"]:
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

        if action == "like" and to_user_id is not None:
            # Get the target user
            to_user = User.objects.filter(id=to_user_id).first()
            
            # If target is a mock user, auto-reciprocate the like
            if to_user and to_user.username.startswith("mock_"):
                Swipe.objects.get_or_create(
                    from_user=to_user,
                    to_user=user,
                    defaults={"action": "like"},
                )
            
            # Check for mutual like
            mutual: bool = Swipe.objects.filter(
                from_user_id=to_user_id,
                to_user=user,
                action="like",
            ).exists()

            if mutual:
                # Calculate compatibility score for the match
                from .algorithm import calculate_match_score
                
                compatibility_score = 0
                shared_tags_count = 0
                shared_interests_count = 0
                compatibility_breakdown: dict[str, Any] = {}
                
                if to_user:
                    score, breakdown = calculate_match_score(user, to_user)
                    compatibility_score = score
                    shared_tags_count = breakdown.shared_tags_count
                    shared_interests_count = breakdown.shared_interests_count
                    compatibility_breakdown = breakdown.to_dict()
                
                # Create match with compatibility data
                match = Match.objects.create(
                    user1=user,
                    user2_id=to_user_id,
                    compatibility_score=compatibility_score,
                    shared_tags_count=shared_tags_count,
                    shared_interests_count=shared_interests_count,
                    compatibility_breakdown=compatibility_breakdown,
                )

                # Create conversation for the match
                Conversation.objects.create(match=match)
                
                # Refresh match from DB to get the conversation relationship
                match.refresh_from_db()

                is_match = True

        response_data: dict[str, Any] = {
            "swipe": SwipeSerializer(swipe).data,
            "is_match": is_match,
        }

        if is_match and match:
            # Prefetch conversation to ensure it's available for serialization
            match = Match.objects.select_related('conversation').get(pk=match.pk)
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


class ShortcutListCreateView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """List or save built-in chat shortcuts for the current user."""

    serializer_class = ShortcutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet[ShortcutResponse]:
        user = cast(User, self.request.user)
        return ShortcutResponse.objects.filter(user=user)

    def perform_create(self, serializer: ShortcutSerializer) -> None:
        serializer.save(user=self.request.user)


class ShortcutDeleteView(APIView):
    """Remove a saved shortcut for the current user."""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request, shortcut_id: int) -> Response:
        user = cast(User, request.user)
        shortcut = ShortcutResponse.objects.filter(user=user, id=shortcut_id).first()
        if not shortcut:
            return Response(
                {"error": "Shortcut not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        shortcut.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        import logging
        logger = logging.getLogger(__name__)
        
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
        
        # Check if the other user is a mock user and generate AI response
        # Wrap in try-except to not fail the user's message if AI fails
        try:
            self._generate_mock_user_response(conversation, user, message.content)
        except Exception as e:
            logger.error(f"Failed to generate mock user response: {e}")

        return Response(
            MessageSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
    
    def _generate_mock_user_response(
        self, conversation: Conversation, sender: User, user_message: str
    ) -> None:
        """Generate an AI response if the conversation partner is a mock user."""
        from .ai_service import generate_ai_response
        
        # Get the other user in the conversation
        match = conversation.match
        other_user: Optional[User] = None
        
        if match.user1 == sender:
            other_user = match.user2
        else:
            other_user = match.user1
        
        # Check if the other user is a mock user
        if not other_user or not other_user.username.startswith("mock_"):
            return
        
        # Get the mock user's profile
        try:
            mock_profile = other_user.profile
        except Exception:
            return
        
        # Get the real user's profile for context
        real_user_profile = None
        try:
            real_user_profile = sender.profile
        except Exception:
            pass  # Continue without real user context
        
        # Build full conversation history
        history: list[dict[str, str]] = []
        messages = conversation.messages.order_by("sent_at").select_related("sender")
        
        for msg in messages:
            role = "assistant" if msg.sender == other_user else "user"
            history.append({"role": role, "content": msg.content})
        
        # Generate AI response with full context
        ai_response = generate_ai_response(
            mock_profile=mock_profile,
            user_message=user_message,
            conversation_history=history,
            real_user_profile=real_user_profile,
        )
        
        if ai_response:
            # Create the AI response as a message from the mock user
            Message.objects.create(
                conversation=conversation,
                sender=other_user,
                content=ai_response,
            )
            # Update conversation timestamp
            conversation.save()


class ConversationSuggestionsView(APIView):
    """Generate AI reply suggestions for a conversation."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, conversation_id: int) -> Response:
        user = cast(User, request.user)
        conversation = _get_conversation_for_user(user, conversation_id)
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(user, "profile") or not user.profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        other_user = (
            conversation.match.user2
            if conversation.match.user1_id == user.id
            else conversation.match.user1
        )
        if not hasattr(other_user, "profile") or not other_user.profile:
            return Response(
                {"error": "Match profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use the last 20 messages for richer suggestions
        messages = list(
            Message.objects.filter(conversation=conversation)
            .order_by("-sent_at")[:20]
        )
        history = _build_conversation_history(reversed(messages), user)

        suggestions = generate_message_suggestions(
            conversation_history=history,
            user_profile=user.profile,
            other_profile=other_user.profile,
            language_code=_get_request_language(request),
        )

        if not suggestions:
            suggestions = []

        return Response({"suggestions": suggestions})


class ConversationSummaryView(APIView):
    """Generate AI summary for a conversation."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, conversation_id: int) -> Response:
        user = cast(User, request.user)
        conversation = _get_conversation_for_user(user, conversation_id)
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not hasattr(user, "profile") or not user.profile:
            return Response(
                {"error": "Profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        other_user = (
            conversation.match.user2
            if conversation.match.user1_id == user.id
            else conversation.match.user1
        )
        if not hasattr(other_user, "profile") or not other_user.profile:
            return Response(
                {"error": "Match profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        messages = list(
            Message.objects.filter(conversation=conversation)
            .order_by("-sent_at")[:30]
        )
        history = _build_conversation_history(reversed(messages), user)

        summary = generate_conversation_summary(
            conversation_history=history,
            user_profile=user.profile,
            other_profile=other_user.profile,
            language_code=_get_request_language(request),
        )
        if not summary:
            summary = ""

        return Response({"summary": summary})


class ConversationTypingView(APIView):
    """Typing indicator endpoint."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request, conversation_id: int) -> Response:
        user = cast(User, request.user)
        conversation = _get_conversation_for_user(user, conversation_id)
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        other_user = (
            conversation.match.user2
            if conversation.match.user1_id == user.id
            else conversation.match.user1
        )
        key = f"typing:{conversation_id}:{other_user.id}"
        is_typing = bool(cache.get(key))
        return Response({"is_typing": is_typing, "user_id": other_user.id})

    def post(self, request: Request, conversation_id: int) -> Response:
        user = cast(User, request.user)
        conversation = _get_conversation_for_user(user, conversation_id)
        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        is_typing = bool(request.data.get("is_typing", True))
        key = f"typing:{conversation_id}:{user.id}"

        if is_typing:
            cache.set(key, True, timeout=8)
        else:
            cache.delete(key)

        return Response({"ok": True, "is_typing": is_typing})

class VoiceMessageUploadView(APIView):
    """Upload voice message for a conversation."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_conversation(self, user: User, conversation_id: int) -> Optional[Conversation]:
        """Get conversation if user is a participant."""
        return (
            Conversation.objects.filter(id=conversation_id)
            .filter(Q(match__user1=user) | Q(match__user2=user))
            .first()
        )

    def post(self, request: Request, conversation_id: int) -> Response:
        """Upload a voice message."""
        user = cast(User, request.user)
        conversation = self.get_conversation(user, conversation_id)

        if not conversation:
            return Response(
                {"error": "Conversation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = VoiceMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        audio_file = serializer.validated_data["audio"]
        duration = serializer.validated_data.get("duration", 0)
        transcript = serializer.validated_data.get("transcript", "")

        try:
            # Upload to Cloudinary
            import cloudinary.uploader

            upload_result = cloudinary.uploader.upload(
                audio_file,
                resource_type="video",  # Cloudinary uses 'video' for audio
                folder="nomi/voice_messages",
                format="mp3",
            )
            audio_url = upload_result.get("secure_url", "")

            if not audio_url:
                return Response(
                    {"error": "Failed to upload audio"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Create the message
            message = Message.objects.create(
                conversation=conversation,
                sender=user,
                message_type="voice",
                content="🎤 Voice message",
                audio_url=audio_url,
                audio_duration=duration,
                transcript=transcript,
            )

            # Update conversation timestamp
            conversation.save()

            logger.info(f"Voice message uploaded: {message.id} by user {user.id}")

            return Response(
                MessageSerializer(message, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )

        except ImportError:
            logger.error("Cloudinary not installed")
            return Response(
                {"error": "Voice messages not configured"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error uploading voice message: {e}")
            return Response(
                {"error": "Failed to upload voice message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


class UnmatchView(APIView):
    """Disconnect/unmatch from a specific match."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request, match_id: int) -> Response:
        user = cast(User, request.user)

        # Get the match and verify user is part of it
        match: Optional[Match] = Match.objects.filter(
            Q(user1=user) | Q(user2=user),
            id=match_id,
        ).first()

        if not match:
            return Response(
                {"error": "Match not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Delete all messages in the conversation
        messages_deleted: int = 0
        try:
            conversation = match.conversation
            messages_deleted = conversation.messages.count()
            conversation.messages.all().delete()
            # Delete the conversation itself
            conversation.delete()
        except Conversation.DoesNotExist:
            pass

        # Delete swipes between the two users (so they can rematch later)
        Swipe.objects.filter(
            Q(from_user=match.user1, to_user=match.user2) |
            Q(from_user=match.user2, to_user=match.user1)
        ).delete()

        # Delete the match entirely (or set is_active=False if you want to keep history)
        match.delete()

        return Response({
            "message": "Successfully disconnected",
            "deleted": {
                "messages": messages_deleted,
            }
        })


class CleanupView(APIView):
    """Clean up all matching data for the current user."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user = cast(User, request.user)

        # Delete messages sent by user
        message_count: int = Message.objects.filter(sender=user).count()
        Message.objects.filter(sender=user).delete()

        # Get user's matches
        user_matches = Match.objects.filter(Q(user1=user) | Q(user2=user))

        # Delete conversations from these matches
        conversation_count: int = Conversation.objects.filter(
            match__in=user_matches
        ).count()
        Conversation.objects.filter(match__in=user_matches).delete()

        # Delete matches
        match_count: int = user_matches.count()
        user_matches.delete()

        # Delete swipes
        swipe_count: int = Swipe.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        ).count()
        Swipe.objects.filter(Q(from_user=user) | Q(to_user=user)).delete()

        return Response({
            "message": "Cleanup complete",
            "deleted": {
                "messages": message_count,
                "conversations": conversation_count,
                "matches": match_count,
                "swipes": swipe_count,
            }
        })
