import os
import socket
from pathlib import Path

from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = int(os.environ.get("DEBUG", 1))
APP_DESCRIPTION = os.environ.get("APP_DESCRIPTION", "Lincride API")
ALLOWED_HOSTS = [
    "127.0.0.1",
    "0.0.0.0",
    "localhost",
    "api",
    "host.docker.internal",
]
INTERNAL_IPS = ["127.0.0.1"]
if DEBUG:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "storages",
    "rest_framework",
    "rest_framework_api_key",
    "django_filters",
    "import_export",
    "debug_toolbar",
    "drf_spectacular",
    "django_extensions",
    "django_celery_beat",
    "core.celery.CeleryConfig",
    "user.apps.UserConfig",
    "trip.apps.TripConfig",
    "location.apps.LocationConfig",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.ValidationErrorMiddleware",

]

AUTH_USER_MODEL = "user.User"
ROOT_URLCONF = "core.urls"
IMPORT_EXPORT_USE_TRANSACTIONS = True

SAFE_LIST_IPS = os.getenv("SAFE_LIST_IPS", "").split(",")

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

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [

]
CORS_ALLOW_HEADERS = list(default_headers) + ["X-Api-Key"]
LOGIN_URL = "rest_framework:login"
LOGOUT_URL = "rest_framework:logout"

JAZZMIN_SETTINGS = {
    "site_title": APP_DESCRIPTION,
    "site_header": APP_DESCRIPTION,
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

# Email Settings
DEFAULT_EMAIL_SERVICE = os.environ.get(
    "DEFAULT_EMAIL_SERVICE", "ELASTIC"
)  # UNIONE, ELASTIC, SENDGRID,

EMAIL_FROM = os.environ.get(f"{DEFAULT_EMAIL_SERVICE}_SENDER_EMAIL")
DEFAULT_FROM_EMAIL = f"<{EMAIL_FROM}>"
EMAIL_HOST = os.environ.get(f"{DEFAULT_EMAIL_SERVICE}_SMTP_HOST")
EMAIL_HOST_USER = os.environ.get(f"{DEFAULT_EMAIL_SERVICE}_SMTP_USER")
EMAIL_HOST_PASSWORD = os.environ.get(f"{DEFAULT_EMAIL_SERVICE}_SMTP_PASSWORD")
EMAIL_PORT = os.environ.get(f"{DEFAULT_EMAIL_SERVICE}_SMTP_PORT", 587)
EMAIL_USE_TLS = True

# Others
TOKEN_LIFESPAN = 24 * 7  # hours
CLIENT_URL = os.environ.get("CLIENT_URL")

ENVIRONMENT_INSTANCE = os.environ.get("ENVIRONMENT_INSTANCE", "dev")
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH', '/usr/lib/libgdal.so')
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
GOOGLE_MAPS_ROUTE_URL = os.environ.get("GOOGLE_MAPS_ROUTE_URL", "https://routes.googleapis.com/directions/v2")
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
