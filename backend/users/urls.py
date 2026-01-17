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
    # Current user
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("language/", views.UpdateLanguageView.as_view(), name="update-language"),
    # Session management
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("validate/", views.ValidateTokenView.as_view(), name="validate-token"),
]
