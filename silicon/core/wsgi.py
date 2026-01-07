"""WSGI config for quiz project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Set APP_MODE if not already set
if not os.environ.get("APP_MODE"):
    os.environ.setdefault("APP_MODE", "prod")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "silicon.core.settings")

application = get_wsgi_application()
