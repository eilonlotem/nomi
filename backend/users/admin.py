from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpRequest

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):  # type: ignore[type-arg]
    """Admin configuration for custom User model."""

    list_display = [
        "username",
        "email",
        "social_provider",
        "preferred_language",
        "is_verified",
        "is_profile_complete",
        "is_active",
        "last_active",
    ]

    list_filter = [
        "social_provider",
        "preferred_language",
        "is_verified",
        "is_profile_complete",
        "is_active",
        "is_staff",
    ]

    search_fields = ["username", "email", "first_name", "last_name"]

    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore[operator]
        ("Social Auth", {"fields": ("social_provider", "social_id")}),
        ("Profile", {"fields": ("phone_number", "date_of_birth", "preferred_language")}),
        ("Status", {"fields": ("is_verified", "is_profile_complete", "last_active")}),
    )

    readonly_fields = ("last_active", "created_at", "updated_at")

    def get_readonly_fields(
        self, request: HttpRequest, obj: Any = None
    ) -> tuple[str, ...]:
        return self.readonly_fields
