# Copyright 2021 Pants project contributors.
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

import os
from pathlib import Path
from tempfile import mkdtemp

from django.conf import settings

from silicon._settings import test

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def configure_settings(apps: list[str]) -> None:
    """Minimal settings for unittests."""
    apps += (
        "fcm_django",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    )
    settings.configure(
        TESTING=True,
        SECRET_KEY="DEV_SECURITY_KEY",
        TIME_ZONE="UTC",
        USE_TZ=True,
        FIREBASE_CRED_PATH="/home/gprao/projects/silicon/firebase_dev.json",
        ROOT_URLCONF="silicon._microservices.admin.urls",
        INSTALLED_APPS=apps,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": os.path.join(
                    mkdtemp(),
                    f"test{os.environ.get('PANTS_EXECUTION_SLOT', '')}.sqlite3",
                ),
            }
        },
        AUTH_USER_MODEL="users.CustomUser",
        MIDDLEWARE=[  # noqa: F405
            "django.contrib.sessions.middleware.SessionMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        NINJA_EXTRA={
            "INJECTOR_MODULES": [
                "silicon._sdk._modules.RepositoryModule",
                "silicon._sdk._modules.ServiceModule",
            ]
        },
    )
