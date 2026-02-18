from __future__ import annotations

from typing import Any

from django.contrib import admin, messages
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Block, Conversation, Match, Message, Swipe
from .support import SUPPORT_USERNAME


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_support_user():  # type: ignore[no-untyped-def]
    from users.models import User
    return User.objects.filter(username=SUPPORT_USERNAME).first()


# ---------------------------------------------------------------------------
# Custom admin action
# ---------------------------------------------------------------------------

@admin.action(description="Delete ALL matches, swipes, messages & conversations")
def clear_all_matching_data(
    modeladmin: Any, request: HttpRequest, queryset: Any
) -> None:
    msg_count = Message.objects.count()
    conv_count = Conversation.objects.count()
    match_count = Match.objects.count()
    swipe_count = Swipe.objects.count()

    Message.objects.all().delete()
    Conversation.objects.all().delete()
    Match.objects.all().delete()
    Swipe.objects.all().delete()

    messages.success(
        request,
        f"Cleared: {msg_count} messages, {conv_count} conversations, "
        f"{match_count} matches, {swipe_count} swipes",
    )


# ---------------------------------------------------------------------------
# Swipe
# ---------------------------------------------------------------------------

@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["from_user", "to_user", "action", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["from_user__username", "to_user__username"]
    date_hierarchy = "created_at"
    actions = [clear_all_matching_data]


# ---------------------------------------------------------------------------
# Match
# ---------------------------------------------------------------------------

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "user1",
        "user2",
        "compatibility_score",
        "shared_tags_count",
        "is_active",
        "matched_at",
    ]
    list_filter = ["is_active", "matched_at"]
    search_fields = ["user1__username", "user2__username"]
    date_hierarchy = "matched_at"
    actions = [clear_all_matching_data]

    change_list_template = "admin/matching/match/change_list.html"

    def get_urls(self) -> list[Any]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "clear-all/",
                self.admin_site.admin_view(self.clear_all_view),
                name="matching_match_clear_all",
            ),
        ]
        return custom_urls + urls

    def clear_all_view(self, request: HttpRequest) -> HttpResponseRedirect:
        msg_count = Message.objects.count()
        conv_count = Conversation.objects.count()
        match_count = Match.objects.count()
        swipe_count = Swipe.objects.count()

        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Match.objects.all().delete()
        Swipe.objects.all().delete()

        messages.success(
            request,
            f"Cleared: {msg_count} messages, {conv_count} conversations, "
            f"{match_count} matches, {swipe_count} swipes",
        )
        return HttpResponseRedirect(reverse("admin:matching_match_changelist"))


# ---------------------------------------------------------------------------
# Message (inline)
# ---------------------------------------------------------------------------

class MessageInline(admin.TabularInline):  # type: ignore[type-arg]
    model = Message
    extra = 0
    readonly_fields = ["sender", "content", "sent_at", "is_read"]
    can_delete = False


# ---------------------------------------------------------------------------
# Conversation — with support-reply functionality
# ---------------------------------------------------------------------------

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "id",
        "match",
        "is_support_conversation",
        "other_user_display",
        "message_count",
        "last_message_preview",
        "reply_link",
        "updated_at",
    ]
    list_filter = ["created_at", "updated_at"]
    search_fields = [
        "match__user1__username",
        "match__user2__username",
        "match__user1__profile__display_name",
        "match__user2__profile__display_name",
    ]
    inlines = [MessageInline]

    change_list_template = "admin/matching/conversation/change_list.html"

    def get_urls(self) -> list[Any]:
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:conversation_id>/reply/",
                self.admin_site.admin_view(self.reply_as_support_view),
                name="matching_conversation_reply",
            ),
        ]
        return custom_urls + urls

    # -- custom columns -------------------------------------------------------

    def is_support_conversation(self, obj: Conversation) -> bool:
        return (
            obj.match.user1.username == SUPPORT_USERNAME
            or obj.match.user2.username == SUPPORT_USERNAME
        )
    is_support_conversation.boolean = True  # type: ignore[attr-defined]
    is_support_conversation.short_description = "Support"  # type: ignore[attr-defined]

    def other_user_display(self, obj: Conversation) -> str:
        u1 = obj.match.user1
        u2 = obj.match.user2
        if u1.username == SUPPORT_USERNAME:
            other = u2
        elif u2.username == SUPPORT_USERNAME:
            other = u1
        else:
            return f"{u1} & {u2}"
        name = getattr(getattr(other, "profile", None), "display_name", other.username)
        return str(name)
    other_user_display.short_description = "User"  # type: ignore[attr-defined]

    def message_count(self, obj: Conversation) -> int:
        return obj.messages.count()
    message_count.short_description = "Messages"  # type: ignore[attr-defined]

    def last_message_preview(self, obj: Conversation) -> str:
        last = obj.messages.order_by("-sent_at").first()
        if not last:
            return "-"
        prefix = "You" if last.sender.username == SUPPORT_USERNAME else last.sender.username
        text = last.content[:60] + ("..." if len(last.content) > 60 else "")
        return f"[{prefix}] {text}"
    last_message_preview.short_description = "Last message"  # type: ignore[attr-defined]

    def reply_link(self, obj: Conversation) -> str:
        is_support = (
            obj.match.user1.username == SUPPORT_USERNAME
            or obj.match.user2.username == SUPPORT_USERNAME
        )
        if not is_support:
            return "-"
        url = reverse("admin:matching_conversation_reply", args=[obj.id])
        return format_html('<a href="{}" style="font-weight:bold;">Reply</a>', url)
    reply_link.short_description = "Reply"  # type: ignore[attr-defined]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Conversation]:
        qs = super().get_queryset(request)
        return qs.select_related(
            "match",
            "match__user1",
            "match__user2",
            "match__user1__profile",
            "match__user2__profile",
        )

    # -- reply view -----------------------------------------------------------

    def reply_as_support_view(
        self, request: HttpRequest, conversation_id: int
    ) -> HttpResponse:
        conversation = Conversation.objects.select_related(
            "match", "match__user1", "match__user2",
            "match__user1__profile", "match__user2__profile",
        ).filter(id=conversation_id).first()

        if not conversation:
            messages.error(request, "Conversation not found.")
            return HttpResponseRedirect(
                reverse("admin:matching_conversation_changelist")
            )

        support_user = _get_support_user()
        if not support_user:
            messages.error(request, "Support user does not exist. Run create_support_user command.")
            return HttpResponseRedirect(
                reverse("admin:matching_conversation_changelist")
            )

        u1 = conversation.match.user1
        u2 = conversation.match.user2
        if u1.username == SUPPORT_USERNAME:
            other = u2
        else:
            other = u1
        other_name = getattr(getattr(other, "profile", None), "display_name", other.username)

        if request.method == "POST":
            content = request.POST.get("content", "").strip()
            if content:
                Message.objects.create(
                    conversation=conversation,
                    sender=support_user,
                    content=content,
                )
                conversation.save()
                messages.success(request, f"Reply sent to {other_name}.")
                return HttpResponseRedirect(
                    reverse("admin:matching_conversation_reply", args=[conversation_id])
                )
            else:
                messages.warning(request, "Message cannot be empty.")

        chat_messages = list(
            conversation.messages.order_by("sent_at").select_related("sender")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": f"Support Chat — {other_name}",
            "conversation": conversation,
            "other_name": other_name,
            "chat_messages": chat_messages,
            "support_username": SUPPORT_USERNAME,
            "opts": self.model._meta,
        }

        return TemplateResponse(
            request,
            "admin/matching/conversation/reply.html",
            context,
        )


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "sender",
        "conversation",
        "short_content",
        "message_type",
        "is_read",
        "sent_at",
    ]
    list_filter = ["message_type", "is_read", "sent_at"]
    search_fields = ["content", "sender__username"]
    date_hierarchy = "sent_at"

    def short_content(self, obj: Message) -> str:
        if len(obj.content) > 80:
            return obj.content[:80] + "..."
        return obj.content
    short_content.short_description = "Content"  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Block
# ---------------------------------------------------------------------------

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["blocker", "blocked", "reason", "created_at"]
    list_filter = ["reason", "created_at"]
    search_fields = ["blocker__username", "blocked__username"]
