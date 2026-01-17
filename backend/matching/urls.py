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
    # Conversations
    path(
        "conversations/", views.ConversationListView.as_view(), name="conversations-list"
    ),
    path(
        "conversations/<int:conversation_id>/messages/",
        views.ConversationMessagesView.as_view(),
        name="conversation-messages",
    ),
    # Block
    path("block/", views.BlockUserView.as_view(), name="block-user"),
    path("block/<int:user_id>/", views.BlockUserView.as_view(), name="unblock-user"),
]
