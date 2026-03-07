import os
from pathlib import Path

# ===================================================
# BASE DIRECTORY
# ===================================================
BASE_DIR = Path(__file__).resolve().parent.parent


# ===================================================
# SECURITY
# ===================================================
SECRET_KEY = 'django-insecure-piemr-sports-portal-change-this-in-production-2026'

DEBUG = True

ALLOWED_HOSTS = ['*']


# ===================================================
# INSTALLED APPS
# ===================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sports_app',
]


# ===================================================
# MIDDLEWARE
# ===================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ===================================================
# URL CONFIGURATION
# ===================================================
ROOT_URLCONF = 'sports_portal.urls'


# ===================================================
# TEMPLATES
# ===================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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


# ===================================================
# WSGI
# ===================================================
WSGI_APPLICATION = 'sports_portal.wsgi.application'


# ===================================================
# DATABASE — Using SQLite for now (easy, no setup)
# Switch to PostgreSQL later for deployment
# ===================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ===================================================
# POSTGRESQL (Uncomment this and comment SQLite above
# when you are ready to deploy)
# ===================================================
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'sports_db',
#         'USER': 'postgres',
#         'PASSWORD': 'your_password_here',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# ===================================================
# PASSWORD VALIDATION
# ===================================================
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


# ===================================================
# INTERNATIONALIZATION
# ===================================================
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# ===================================================
# STATIC FILES (CSS, JavaScript, Images)
# ===================================================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# ===================================================
# MEDIA FILES (User uploaded images)
# ===================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ===================================================
# LOGIN / LOGOUT REDIRECTS
# ===================================================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'


# ===================================================
# EMAIL (Console backend for development)
# ===================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ===================================================
# DEFAULT PRIMARY KEY
# ===================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===================================================
# MESSAGE TAGS (for Bootstrap alert classes)
# ===================================================
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG:   'secondary',
    messages.INFO:    'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR:   'danger',
}
# Email for password reset (console for now)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'PIEMR Sports Portal <51110105688@piemr.edu.in>'
import os

# Production settings
ALLOWED_HOSTS = ['*']

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security (Railway sets DEBUG=False automatically)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)