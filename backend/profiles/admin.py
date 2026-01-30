from __future__ import annotations

from django.contrib import admin

from .models import (
    DisabilityTag,
    Interest,
    LookingFor,
    Profile,
    ProfileDisabilityTagVisibility,
    ProfilePhoto,
)


@admin.register(DisabilityTag)
class DisabilityTagAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "code",
        "name_en",
        "icon",
        "category",
        "disclosure_level",
        "is_active",
        "order",
    ]
    list_editable = ["is_active", "order"]
    search_fields = ["code", "name_en", "category"]
    ordering = ["order"]


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["name", "icon", "category"]
    list_filter = ["category"]
    search_fields = ["name"]
    ordering = ["category", "name"]


class ProfilePhotoInline(admin.TabularInline):  # type: ignore[type-arg]
    model = ProfilePhoto
    extra = 0
    readonly_fields = ["uploaded_at"]


class LookingForInline(admin.StackedInline):  # type: ignore[type-arg]
    model = LookingFor
    can_delete = False


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = [
        "display_name",
        "user",
        "gender",
        "city",
        "current_mood",
        "is_visible",
        "created_at",
    ]

    list_filter = ["is_visible", "current_mood", "gender", "city"]
    search_fields = ["display_name", "user__username", "user__email", "city"]

    readonly_fields = ["created_at", "updated_at"]

    filter_horizontal = ["disability_tags", "interests"]

    inlines = [ProfilePhotoInline, LookingForInline]

    fieldsets = (
        (None, {"fields": ("user", "display_name", "bio")}),
        ("Personal", {"fields": ("gender", "date_of_birth")}),
        ("Location", {"fields": ("city", "country", "latitude", "longitude")}),
        (
            "Identity",
            {"fields": ("disability_tags", "interests", "current_mood")},
        ),
        (
            "Intent",
            {"fields": ("relationship_intent", "openness_tags")},
        ),
        ("Prompt", {"fields": ("prompt_id", "prompt_answer")}),
        ("Ask Me About It", {"fields": ("ask_me_prompt_id", "ask_me_answer")}),
        ("Time Preferences", {"fields": ("preferred_times", "response_pace", "date_pace", "time_notes")}),
        ("Settings", {"fields": ("is_visible", "show_distance", "picture_url")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["profile", "is_primary", "order", "uploaded_at"]
    list_filter = ["is_primary"]
    search_fields = ["profile__display_name"]


@admin.register(ProfileDisabilityTagVisibility)
class ProfileDisabilityTagVisibilityAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["profile", "tag", "visibility", "updated_at"]
    list_filter = ["visibility"]
    search_fields = ["profile__display_name", "tag__code", "tag__name_en"]
