"""
Settings for Narrow Gate, a site of Scripture escape rooms.

There is no database: each team's progress lives in a signed session cookie,
so the app can run on any free Python host with an ephemeral filesystem.

Environment variables:
  DJANGO_SECRET_KEY     Required in production. When it is set, DEBUG defaults off.
  DJANGO_DEBUG          "1" or "0" to override the default.
  DJANGO_ALLOWED_HOSTS  Comma-separated hostnames, e.g. "yourname.pythonanywhere.com".
"""

import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
DEBUG = os.environ.get("DJANGO_DEBUG", "0" if SECRET_KEY else "1") == "1"
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured("Set DJANGO_SECRET_KEY when DEBUG is off.")
    SECRET_KEY = "django-insecure-local-dev-only"

SITE_NAME = "Narrow Gate"
PUBLIC_REPO_URL = "https://github.com/Kai-ssu/narrow-gate-public"
AUTHOR_URL = "https://github.com/Kai-ssu"

# Passcode for every game's answer key (/<game>/lead/answers/). Set it on the host;
# locally it defaults to "philippi". Without one in production the key stays locked.
LEADER_CODE = os.environ.get("LEADER_CODE", "philippi" if DEBUG else "")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
# Render sets this automatically for its web services.
if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
    ALLOWED_HOSTS.append(os.environ["RENDER_EXTERNAL_HOSTNAME"])

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "game",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "narrowgate.urls"
WSGI_APPLICATION = "narrowgate.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "game.context_processors.site",
            ],
        },
    },
]

# No database at all.
DATABASES = {}

# Progress is stored client-side, signed with SECRET_KEY so players can't edit it.
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_AGE = 12 * 60 * 60
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
# Render (and most hosts) terminate HTTPS at a proxy; trust its header so
# absolute links, like the backdrop's QR code, use https://.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_SECURE = not DEBUG

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
