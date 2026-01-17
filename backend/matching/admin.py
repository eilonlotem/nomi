from __future__ import annotations

from django.contrib import admin

from .models import Block, Conversation, Match, Message, Swipe


@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["from_user", "to_user", "action", "created_at"]
    list_filter = ["action", "created_at"]
    search_fields = ["from_user__username", "to_user__username"]
    date_hierarchy = "created_at"


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
