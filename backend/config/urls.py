"""
URL configuration for Nomi backend.
"""
from __future__ import annotations

from typing import Union

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns: list[Union[URLPattern, URLResolver]] = [
    path("admin/", admin.site.urls),
    # API endpoints
    path("api/auth/", include("users.urls", namespace="users")),
    path("api/auth/token/", obtain_auth_token, name="api-token"),
    path("api/profiles/", include("profiles.urls", namespace="profiles")),
    path("api/", include("matching.urls", namespace="matching")),
    # Social authentication (for web OAuth flow)
    path("social/", include("social_django.urls", namespace="social")),
    # DRF browsable API login
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
