"""
Django settings for Nomi backend.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY: str = os.getenv("SECRET_KEY", "django-insecure-dev-key-change-in-production")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS: list[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")


# Application definition

INSTALLED_APPS: list[str] = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "social_django",
    "cloudinary_storage",
    "cloudinary",
    # Local apps
    "users.apps.UsersConfig",
    "profiles.apps.ProfilesConfig",
    "matching.apps.MatchingConfig",
]

MIDDLEWARE: list[str] = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Serve static files in production
    "corsheaders.middleware.CorsMiddleware",  # CORS - must be before CommonMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF: str = "config.urls"

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION: str = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import dj_database_url

# Use PostgreSQL in production if DATABASE_URL is set, otherwise SQLite
DATABASE_URL: str | None = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES: dict[str, dict[str, Any]] = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES: dict[str, dict[str, Any]] = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Custom User Model
AUTH_USER_MODEL: str = "users.User"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE: str = "en-us"

TIME_ZONE: str = "UTC"

USE_I18N: bool = True

USE_TZ: bool = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL: str = "static/"
STATIC_ROOT: Path = BASE_DIR / "staticfiles"

# WhiteNoise for serving static files in production
STATICFILES_STORAGE: str = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (User uploads)
MEDIA_URL: str = "media/"
MEDIA_ROOT: Path = BASE_DIR / "media"

# Production security settings
if not DEBUG:
    SECURE_SSL_REDIRECT: bool = True
    SESSION_COOKIE_SECURE: bool = True
    CSRF_COOKIE_SECURE: bool = True
    SECURE_BROWSER_XSS_FILTER: bool = True
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_HSTS_SECONDS: int = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = True
    SECURE_HSTS_PRELOAD: bool = True
    X_FRAME_OPTIONS: str = "DENY"
    
    # Trust Railway/Render proxy headers
    SECURE_PROXY_SSL_HEADER: tuple[str, str] = ("HTTP_X_FORWARDED_PROTO", "https")


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"


# Django REST Framework
REST_FRAMEWORK: dict[str, Any] = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}


# CORS Settings
CORS_ALLOWED_ORIGINS: list[str] = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

CORS_ALLOW_CREDENTIALS: bool = True

# For development - allow all origins
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS: bool = True


# =============================================================================
# Social Authentication (Facebook, Instagram)
# =============================================================================

AUTHENTICATION_BACKENDS: list[str] = [
    "social_core.backends.facebook.FacebookOAuth2",
    "django.contrib.auth.backends.ModelBackend",
]

# Facebook OAuth2 Configuration
SOCIAL_AUTH_FACEBOOK_KEY: str = os.getenv("FACEBOOK_APP_ID", "")
SOCIAL_AUTH_FACEBOOK_SECRET: str = os.getenv("FACEBOOK_APP_SECRET", "")
SOCIAL_AUTH_FACEBOOK_SCOPE: list[str] = ["email", "public_profile", "user_birthday", "user_gender"]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS: dict[str, str] = {
    "fields": "id,name,email,picture.type(large),first_name,last_name,birthday,gender"
}

# Store extra data from Facebook
SOCIAL_AUTH_FACEBOOK_EXTRA_DATA: list[tuple[str, str]] = [
    ("name", "name"),
    ("email", "email"),
    ("picture", "picture"),
    ("first_name", "first_name"),
    ("last_name", "last_name"),
]

# Social auth pipeline - what happens when user authenticates
SOCIAL_AUTH_PIPELINE: list[str] = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "users.pipeline.create_user_profile",  # Custom pipeline to create profile
]

# Where to redirect after social auth (for web flow)
SOCIAL_AUTH_LOGIN_REDIRECT_URL: str = (
    os.getenv("FRONTEND_URL", "http://localhost:5173") + "/auth/callback"
)
SOCIAL_AUTH_LOGIN_ERROR_URL: str = (
    os.getenv("FRONTEND_URL", "http://localhost:5173") + "/auth/error"
)

# Social auth settings
SOCIAL_AUTH_URL_NAMESPACE: str = "social"
SOCIAL_AUTH_JSONFIELD_ENABLED: bool = True

# Use custom user model
SOCIAL_AUTH_USER_MODEL: str = "users.User"

# =============================================================================
# OpenAI Configuration (for AI-powered mock user responses)
# =============================================================================

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Also expose Facebook credentials without the SOCIAL_AUTH prefix for our custom views
FACEBOOK_APP_ID: str = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET: str = os.getenv("FACEBOOK_APP_SECRET", "")

# Frontend URL for redirects
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

# =============================================================================
# Cloudinary Configuration (for image uploads)
# =============================================================================

CLOUDINARY_STORAGE: dict[str, str] = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET", ""),
}

# Use Cloudinary for media files in production
if os.getenv("CLOUDINARY_CLOUD_NAME"):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
