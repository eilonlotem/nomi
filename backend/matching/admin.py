from __future__ import annotations

from typing import Any

from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import path, reverse

from .models import Block, Conversation, Match, Message, Swipe


# Custom admin action to delete all selected items
@admin.action(description="Delete ALL matches, swipes, messages & conversations")
def clear_all_matching_data(
    modeladmin: Any, request: HttpRequest, queryset: Any
) -> None:
    """Admin action to clear all matching data."""
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


@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["from_user", "to_user", "action", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["from_user__username", "to_user__username"]
    date_hierarchy = "created_at"
    actions = [clear_all_matching_data]


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
        """View to clear all matching data."""
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
            f"✅ Cleared: {msg_count} messages, {conv_count} conversations, "
            f"{match_count} matches, {swipe_count} swipes",
        )
        return HttpResponseRedirect(reverse("admin:matching_match_changelist"))


class MessageInline(admin.TabularInline):  # type: ignore[type-arg]
    model = Message
    extra = 0
    readonly_fields = ["sender", "content", "sent_at", "is_read"]
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["match", "message_count", "created_at", "updated_at"]
    search_fields = ["match__user1__username", "match__user2__username"]
    inlines = [MessageInline]

    def message_count(self, obj: Conversation) -> int:
        return obj.messages.count()

    message_count.short_description = "Messages"  # type: ignore[attr-defined]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "sender",
        "conversation",
        "message_type",
        "is_read",
        "sent_at",
    ]
    list_filter = ["message_type", "is_read", "sent_at"]
    search_fields = ["content", "sender__username"]
    date_hierarchy = "sent_at"


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["blocker", "blocked", "reason", "created_at"]
    list_filter = ["reason", "created_at"]
    search_fields = ["blocker__username", "blocked__username"]
