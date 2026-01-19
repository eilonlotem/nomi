from __future__ import annotations

from django.urls import URLPattern, path

from . import views

app_name: str = "users"

urlpatterns: list[URLPattern] = [
    # Registration
    path("register/", views.UserRegistrationView.as_view(), name="register"),
    # Social authentication
    path("social/", views.SocialAuthView.as_view(), name="social-auth"),
    path("facebook/", views.FacebookAuthView.as_view(), name="facebook-auth"),
    # Facebook data deletion callback
    path("facebook/data-deletion/", views.FacebookDataDeletionView.as_view(), name="facebook-data-deletion"),
    # Facebook friends and invitations
    path("facebook/friends/", views.FacebookFriendsView.as_view(), name="facebook-friends"),
    path("invitations/", views.InvitationsView.as_view(), name="invitations"),
    path("invitations/stats/", views.InvitationStatsView.as_view(), name="invitation-stats"),
    # Current user
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("language/", views.UpdateLanguageView.as_view(), name="update-language"),
    path("onboarding/complete/", views.CompleteOnboardingView.as_view(), name="complete-onboarding"),
    # Session management
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("validate/", views.ValidateTokenView.as_view(), name="validate-token"),
]
