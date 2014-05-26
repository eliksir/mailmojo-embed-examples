"""
Django settings for demo project.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = '_%giz7*=p-r+*rv3rn&)es3&msrq(8^itl@qop$boc46@a0i_-'


DEBUG = False
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = ['mm-api-demo.e5r.no']
INTERNAL_IPS = ['134.90.144.118', '84.215.96.200', '77.40.215.202']

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'demo',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS =(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
)

ROOT_URLCONF = 'demo.urls'

WSGI_APPLICATION = 'demo.wsgi.application'

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = '/home/e5r/domains/mm-api-demo.e5r.no/public_html/prod'


# Demo app

VERSION = '0.4'
CSS_URL = 'http://mm-api-demo.e5r.no/static/newsletter.css?v={}'.format(VERSION)


# MailMojo OAuth 2.0

API_BASE_URL = 'https://api.mailmojo.no'
API_TOKEN_URL = '{}/oauth/token'.format(API_BASE_URL)
API_GRANT_URL = '{}/oauth/grant_code'.format(API_BASE_URL)

CLIENT_ID = 'ac12f326-e37d-46b2-b4eb-e6aec767ed38'
CLIENT_SECRET = 'test1234'


# Import local settings if they exist

try:
    from local_settings import *
except ImportError:
    pass

