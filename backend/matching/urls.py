from __future__ import annotations

from django.urls import URLPattern, path

from . import views

app_name: str = "matching"

urlpatterns: list[URLPattern] = [
    # Discovery
    path("discover/", views.DiscoveryView.as_view(), name="discover"),
    path("swipe/", views.SwipeView.as_view(), name="swipe"),
    # Matches
    path("matches/", views.MatchListView.as_view(), name="matches-list"),
    path("matches/<int:match_id>/unmatch/", views.UnmatchView.as_view(), name="unmatch"),
    # Conversations
    path(
        "conversations/", views.ConversationListView.as_view(), name="conversations-list"
    ),
    # Shortcuts
    path("shortcuts/", views.ShortcutListCreateView.as_view(), name="shortcuts-list"),
    path(
        "shortcuts/<int:shortcut_id>/",
        views.ShortcutDeleteView.as_view(),
        name="shortcuts-delete",
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        views.ConversationMessagesView.as_view(),
        name="conversation-messages",
    ),
    path(
        "conversations/<int:conversation_id>/suggestions/",
        views.ConversationSuggestionsView.as_view(),
        name="conversation-suggestions",
    ),
    path(
        "conversations/<int:conversation_id>/summary/",
        views.ConversationSummaryView.as_view(),
        name="conversation-summary",
    ),
    path(
        "conversations/<int:conversation_id>/typing/",
        views.ConversationTypingView.as_view(),
        name="conversation-typing",
    ),
    path(
        "conversations/<int:conversation_id>/voice/",
        views.VoiceMessageUploadView.as_view(),
        name="voice-message-upload",
    ),
    # Block
    path("block/", views.BlockUserView.as_view(), name="block-user"),
    path("block/<int:user_id>/", views.BlockUserView.as_view(), name="unblock-user"),
    # Cleanup
    path("cleanup/", views.CleanupView.as_view(), name="cleanup"),
]
