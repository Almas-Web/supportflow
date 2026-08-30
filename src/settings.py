from datetime import timedelta
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-nbb4wqze^$p+bo2y_s(uf%e7(ks!ay_h(j6yw&+fi9gwsv^xf8")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",
    "account",
    "organizations",
    "teams",
    "customers",
    "tickets",
    "sla",
    "notifications.apps.NotificationsConfig",
    "ratings",
    "audit",
    "analytics",
    "reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "src.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "src.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

AUTH_USER_MODEL = "account.CustomUser"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SupportFlow API",
    "DESCRIPTION": "Multi-tenant customer support and ticket management API.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "TAGS": [
        {"name": "Account", "description": "Authentication and user account management."},
        {"name": "Organizations", "description": "Organization and membership management."},
        {"name": "Teams", "description": "Team and team member management."},
        {"name": "Customers", "description": "Customer management."},
        {"name": "Tickets", "description": "Customer support ticket management."},
        {"name": "SLA", "description": "SLA policy and ticket SLA management."},
        {"name": "Notifications", "description": "Organization notifications."},
        {"name": "Ratings", "description": "Customer and ticket ratings."},
        {"name": "Audit", "description": "Organization audit logs."},
        {"name": "Analytics", "description": "Organization analytics and summaries."},
        {"name": "Reports", "description": "Organization reports."},
    ],
}