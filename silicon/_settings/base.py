import os
from pathlib import Path

import django_stubs_ext
from dotenv import load_dotenv

load_dotenv()
django_stubs_ext.monkeypatch()

__APP_MODE__ = os.environ.get("APP_MODE", "local").lower()


DEBUG = False
TESTING = False

BASE_DIR = Path(__file__).resolve().parent.parent
FIREBASE_CRED_PATH = os.environ.get("FIREBASE_CRED_PATH", "/app/firebase_dev.json")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ninja_extra",
    "corsheaders",
    "markdownfield",
    "storages",
    "silicon.quiz.apps.QuizConfig",
    "silicon.knowledge.apps.KnowledgeConfig",
    "silicon.questions.apps.QuestionsConfig",
    "silicon.slides.apps.SlidesConfig",
    "silicon.user.apps.UserConfig",
    "silicon.authentication.apps.AuthenticationConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "silicon/templates")],
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

# CORS_ALLOW_ALL_ORIGINS = True  # Disabled: Cannot use wildcard with credentials
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8080",  # Frontend development server
    "http://127.0.0.1:8080",  # Frontend development server (127.0.0.1)
]

# Allow credentials (cookies, authorization headers) in CORS requests
CORS_ALLOW_CREDENTIALS = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
AUTH_USER_MODEL = "user.CustomUser"


# serve static files from AWS S3 bucket only if local dev is not true
if not TESTING:
    # Amazon S3 settings for static files
    # https://simpleisbetterthancomplex.com/tutorial/2017/08/01/how-to-setup-amazon-s3-in-a-django-project.html
    # https://www.caktusgroup.com/blog/2014/11/10/Using-Amazon-S3-to-store-your-Django-sites-static-and-media-files/
    AWS_REGION = "ap-south-1"
    AWS_S3_REGION_NAME = "ap-south-1"
    AWS_S3_SIGNATURE_VERSION = "s3v4"
    AWS_STORAGE_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "reva-vidyamitra-dev")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_DEFAULT_ACL = None

    AWS_LOCATION = "static"

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{__APP_MODE__}/media/"
    DEFAULT_FILE_STORAGE = "silicon.util.storage_backends.MediaStorage"

    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    STORAGES = {
        "staticfiles": {
            "BACKEND": STATICFILES_STORAGE,
            "OPTIONS": {},
        },
        "default": {
            "BACKEND": DEFAULT_FILE_STORAGE,
            "OPTIONS": {},
        },
    }
else:
    STATIC_URL = f"/static/"

    MEDIA_URL = f"/media/"

    STATIC_ROOT = os.path.join(BASE_DIR, "static")
