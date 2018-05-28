"""
Django settings for StundenzettelCreator project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logger.critical("No environment variable SECRET_KEY defined. "
                    "See https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECRET_KEY "
                    "for further information")
    exit(-1)

# SECURITY WARNING: don't run with debug turned on in production!
PRODUCTION = os.environ.get('PRODUCTION', False) == 'True'
DEBUG = not PRODUCTION

# Error notification
if not os.environ.get('ADMIN_NAME') and not os.environ.get('ADMIN_EMAIL'):
    logger.error("Environment variables ADMIN_NAME and ADMIN_EMAIL "
                 "are not set. These are important for receiving emails about "
                 "server errors and messages from the contact page")
else:
    ADMINS = [(os.environ.get('ADMIN_NAME'), os.environ.get('ADMIN_EMAIL'))]
    MANAGERS = [(os.environ.get('ADMIN_NAME'), os.environ.get('ADMIN_EMAIL'))]

DEFAULT_FROM_EMAIL = 'StundenzettelCreator <notification@stundenzettel-creator.xyz>'

if DEBUG:
    ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'creator.apps.CreatorConfig',
    'easy_pdf'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'StundenzettelCreator.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'StundenzettelCreator.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timesheets'
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'CET'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# Email
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    if not os.environ.get('SENDGRID_USERNAME') and not os.environ.get('SENDGRID_PASSWORD'):
        logger.error("The environment variables SENDGRID_USERNAME and SENDGRID_PASSWORD "
                     "are not set. Please provision a free sendgrid add-on. Otherwise the "
                     "email subscription and contact features will not function properly.")
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        EMAIL_HOST = 'smtp.sendgrid.net'
        EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
        EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
        EMAIL_PORT = 587
        EMAIL_USE_TLS = True

if PRODUCTION:
    # Deploy stuff
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    # Activate Django-Heroku.
    if os.environ.get('HEROKU', False) == 'True':
        import django_heroku
        django_heroku.settings(locals())

    HOST_NAME = 'http://www.stundenzettel-creator.xyz'
else:
    HOST_NAME = 'http://127.0.0.1:8000'
