import os
import sys

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../../'))
sys.path.append(os.path.join(BASE_DIR, 'academy', 'src'))

SECRET_KEY = 'k@^%p5)@&p46+o3ae%99h_&qbr9g+^!@4h5lnlf5!k(=1&n=2v'

ALLOWED_HOSTS = ['*']

# use local.py to change settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db_name',
        'USER': 'db_user',
        'PASSWORD': 'password',
        'HOST': 'db_host',
        'PORT': 'db_port',  # default 5432
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'academy_site',
    'academy_admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'academy.src.middleware.MyAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = ('academy.src.backend.MyAuthenticationBackend',)

ROOT_URLCONF = 'academy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
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

WSGI_APPLICATION = 'academy.wsgi.application'


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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = 'academy_site.AuthUser'
REDIRECT_FIELD_NAME = 'next'

ADMIN_URL = '/admin/'
ADMIN_USER_SESSION_KEY = 'admin_user_id'
SITE_USER_SESSION_KEY = 'site_user_id'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'static/'),
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'data/media/')
USER_PHOTOS_DIR_NAME = 'user-photos'
PARTNER_LOGOS_DIR_NAME = 'partner-logos'
CITY_PHOTOS_DIR_NAME = 'city-photos'
THEME_PHOTOS_DIR_NAME = 'theme-photos'

SERVER_EMAIL = 'root@localhost'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

CONTACT_US_SUBJECT = 'Contact with {name}'

INITIAL_ADMIN = {
    'email': 'admin@admin.com',
    'password': 'admin',
    'first_name': 'fname',
    'last_name': 'lname',
}

SITE_SETTINGS = {
    'contact_phone': '1 800-888-999',
    'contact_email': 'info@herstelacademie.be',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'data/logs/logfile.log'),
            'maxBytes': 1024*1024*10,  # 10 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['logfile', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'public': {
            'handlers': ['logfile', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


try:
    print("Importing local settings")
    from .local import *
    print("Success")
except ImportError:
    print("[WARNING] Cannot import local settings")
