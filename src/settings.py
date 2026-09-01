from datetime import timedelta
import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required.")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
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
        "ENGINE": os.getenv(
            "DB_ENGINE",
            "django.db.backends.sqlite3",
        ),
        "NAME": os.getenv(
            "DB_NAME",
            BASE_DIR / "db.sqlite3",
        ),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"

USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "account.CustomUser"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    EMAIL_HOST_USER,
)


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


SPECTACULAR_SETTINGS = {
    "TITLE": "SupportFlow API",
    "DESCRIPTION": (
        "Multi-tenant customer support and ticket management API."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,

    "TAGS": [
        {
            "name": "Account",
            "description": (
                "Authentication and user account management."
            ),
        },
        {
            "name": "Organizations",
            "description": (
                "Organization and membership management."
            ),
        },
        {
            "name": "Teams",
            "description": (
                "Team and team member management."
            ),
        },
        {
            "name": "Customers",
            "description": "Customer management.",
        },
        {
            "name": "Tickets",
            "description": (
                "Customer support and ticket management."
            ),
        },
        {
            "name": "SLA",
            "description": (
                "SLA policy and ticket SLA management."
            ),
        },
        {
            "name": "Notifications",
            "description": "Organization notifications.",
        },
        {
            "name": "Ratings",
            "description": (
                "Customer and ticket ratings."
            ),
        },
        {
            "name": "Audit",
            "description": "Organization audit logs.",
        },
        {
            "name": "Analytics",
            "description": (
                "Organization analytics and summaries."
            ),
        },
        {
            "name": "Reports",
            "description": "Organization reports.",
        },
    ],
}


# Production security settings

if not DEBUG:
    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"