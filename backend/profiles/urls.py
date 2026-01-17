from __future__ import annotations

from django.urls import URLPattern, path

from . import views

app_name: str = "profiles"

urlpatterns: list[URLPattern] = [
    # Tags and interests
    path("tags/", views.DisabilityTagListView.as_view(), name="tags-list"),
    path("interests/", views.InterestListView.as_view(), name="interests-list"),
    # My profile
    path("me/", views.MyProfileView.as_view(), name="my-profile"),
    path("me/mood/", views.UpdateMoodView.as_view(), name="update-mood"),
    path("me/looking-for/", views.LookingForView.as_view(), name="looking-for"),
    # Photos
    path("me/photos/", views.ProfilePhotoUploadView.as_view(), name="upload-photo"),
    path(
        "me/photos/<int:photo_id>/",
        views.ProfilePhotoUploadView.as_view(),
        name="delete-photo",
    ),
    path(
        "me/photos/<int:photo_id>/primary/",
        views.SetPrimaryPhotoView.as_view(),
        name="set-primary-photo",
    ),
]
