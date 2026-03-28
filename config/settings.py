"""
Django settings for Tpulib project.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# XAVFSIZLIK
# =========================
SECRET_KEY = 'django-insecure-change-this-key'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']


# =========================
# INSTALLED APPS
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom app
    'library',
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# URLS
# =========================
ROOT_URLCONF = 'config.urls'


# =========================
# TEMPLATES (MUHIM!)
# =========================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'library.context_processors.admin_dashboard_stats',
            ],
        },
    },
]


# =========================
# WSGI
# =========================
WSGI_APPLICATION = 'config.wsgi.application'


# =========================
# DATABASE
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =========================
# PASSWORD VALIDATION
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # minimal uzunlikni oshirdim
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]


# =========================
# LANGUAGE & TIME
# =========================
LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True
USE_TZ = True


# =========================
# STATIC FILES
# =========================
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =========================
# MEDIA FILES (PDF, rasm)
# =========================
MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# LOGIN SETTINGS
# =========================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/panel/admin/'
LOGOUT_REDIRECT_URL = '/login/'

# =========================
# DEFAULT PRIMARY KEY
# =========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================
# ADMIN PANEL TEXT
# =========================
ADMIN_SITE_HEADER = "Tpulib Admin Panel"
ADMIN_SITE_TITLE = "Tpulib"
ADMIN_INDEX_TITLE = "Kutubxona boshqaruvi"
X_FRAME_OPTIONS = 'SAMEORIGIN'