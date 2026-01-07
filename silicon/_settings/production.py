import os
from pathlib import Path

from silicon._settings.base import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.

INTERNAL_IPS = ("127.0.0.1", "localhost")
SITE_URL = "http://127.0.0.1/"

__VERSION__ = "0.1"
__APP_MODE__ = "prod"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Get allowed hosts from environment or use default
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",") if os.environ.get("ALLOWED_HOSTS") else ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5000",
    "http://localhost:8080",  # Frontend development server
    "http://127.0.0.1:8080",  # Frontend development server
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",  # Next.js frontend
    "http://localhost:5000",
    "http://localhost:8080",  # Frontend development server
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",  # Next.js frontend
    "http://127.0.0.1:8080",  # Frontend development server
    # Add production frontend URL here
    # "https://your-production-frontend.com",
]

# Allow credentials (cookies, authorization headers) in CORS requests
CORS_ALLOW_CREDENTIALS = True

# Application definition


ROOT_URLCONF = "core.urls"


WSGI_APPLICATION = "silicon.core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Support both DATABASE_URL (Fly.io, Heroku style) and individual DB_* variables
import urllib.parse

database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Parse DATABASE_URL: postgres://user:password@host:port/dbname
    parsed = urllib.parse.urlparse(database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path[1:],  # Remove leading '/'
            "USER": parsed.username,
            "PASSWORD": parsed.password,
            "HOST": parsed.hostname,
            "PORT": parsed.port or "5432",
        }
    }
else:
    # Fallback to individual environment variables
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
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

# CORS_ORIGIN_ALLOW_ALL = True
