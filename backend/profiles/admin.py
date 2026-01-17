from __future__ import annotations

from django.contrib import admin

from .models import DisabilityTag, Interest, LookingFor, Profile, ProfilePhoto


@admin.register(DisabilityTag)
class DisabilityTagAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ["code", "name_en", "icon", "is_active", "order"]
    list_editable = ["is_active", "order"]
    search_fields = ["code", "name_en"]
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
        "city",
        "current_mood",
        "is_visible",
        "created_at",
    ]

    list_filter = ["is_visible", "current_mood", "city"]
    search_fields = ["display_name", "user__username", "user__email", "city"]

    readonly_fields = ["created_at", "updated_at"]

    filter_horizontal = ["disability_tags", "interests"]

    inlines = [ProfilePhotoInline, LookingForInline]

    fieldsets = (
        (None, {"fields": ("user", "display_name", "bio")}),
        ("Location", {"fields": ("city", "country", "latitude", "longitude")}),
        ("Identity", {"fields": ("disability_tags", "interests", "current_mood")}),
        ("Prompt", {"fields": ("prompt_id", "prompt_answer")}),
        ("Settings", {"fields": ("is_visible", "show_distance")}),
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
