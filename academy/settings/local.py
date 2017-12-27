from .main import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

SECRET_KEY = 'k@^%p5)@&p46+o3ae%99h_&qbr9g+^!@4h5lnlf5!k(=1&n=2v'

ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ['127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'academy_local',
        'USER': 'academy',
        'PASSWORD': 'academy',
        'HOST': 'localhost',
        'PORT': '',
    }
}

INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '../tmp/newsletters/'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
