"""Django settings for jolpica project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from pathlib import Path
from typing import Literal

import environ  # type: ignore

from .deployment_utils import get_linux_ec2_private_ip

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
READ_DOT_ENV_FILE = True  # env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

DEPLOYMENT_ENV: Literal["LOCAL", "SANDBOX", "BUILD", "PROD"] = env.str("DEPLOYMENT_ENV", default="LOCAL")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if DEPLOYMENT_ENV == "PROD":
    SECRET_KEY = env("DJANGO_SECRET_KEY")
else:
    SECRET_KEY = env("DJANGO_SECRET_KEY", default="jolpica")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False if DEPLOYMENT_ENV == "PROD" else env("DJANGO_DEBUG", default=True)

live = env("LIVE", cast=str, default="localhost,127.0.0.1").split(",")
ALLOWED_HOSTS: list[str] = ["api.jolpi.ca", *live]
if DEPLOYMENT_ENV == "PROD" and (private_ip := get_linux_ec2_private_ip()):
    ALLOWED_HOSTS.append(private_ip)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "jolpica.ergast",
    "jolpica.formula_one",
    "jolpica.ergastapi",
]
if DEPLOYMENT_ENV in ("LOCAL", "SANDBOX"):
    INSTALLED_APPS += ["django_dbml", "fixture_magic"]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jolpica.urls"

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

WSGI_APPLICATION = "jolpica.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {"default": env.db("DATABASE_SECRET_URL", default="postgis://postgres:postgres@localhost/jolpica")}
DATABASES["default"]["ATOMIC_REQUESTS"] = True


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images) using django-storages
# https://docs.djangoproject.com/en/4.2/howto/static-files
# https://django-storages.readthedocs.io/en/latest/
CLOUDFRONT_DOMAIN = env("CLOUDFRONT_DOMAIN", default="jolpi.ca")

STATICFILES_DIRS = [BASE_DIR / "static"]

if not DEBUG:
    # AWS Cloudfront static files
    STATIC_URL = f"{CLOUDFRONT_DOMAIN}/static/"
    STORAGES = {
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                # Credentials needed to run collectstatic command
                "access_key": env("AWS_STATIC_ACCESS_KEY_ID", default="unset"),
                "secret_key": env("AWS_STATIC_SECRET_ACCESS_KEY", default="unset"),
                "bucket_name": env("AWS_STATIC_S3_BUCKET", default="unset"),
                "location": "static",
                "region_name": env("AWS_S3_REGION_NAME", default="eu-west-1"),
                "signature_version": "s3v4",
                "querystring_expire": 604800,
                "custom_domain": CLOUDFRONT_DOMAIN,
            },
        },
    }
else:
    # Locally served static files
    STATIC_URL = "static/"
    STATIC_ROOT = "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# DJANGO REST FRAMEWORK
# Pagination settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 30,
}
