import os

SERVE_STATIC_FILES = True
DEBUG = True

import packages
PSETTINGS = packages.install()


TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.path.join(PSETTINGS.LOCDIR,'djpcms')             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

SECRET_KEY = '9ydnib90%5_reb+*klqo5*y&kozxxp(mdyc(7uqrifa*=(ln$3'
TIME_ZONE             = 'Europe/London'
LANGUAGE_CODE         = 'en-gb'
SITE_ID = 1
USE_I18N = False

DATE_FORMAT            = 'D d M y'
DATETIME_FORMAT        = 'D d M y P'
ADMIN_URL_PREFIX       = '/admin/' 
MEDIA_ROOT = PSETTINGS.MEDIA_ROOT
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = MEDIA_URL + 'django_admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "djpcms.core.context_processors.djpcms"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'sitedjpcms.urls'



INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.sites',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  'django.contrib.admin',
                  'djpcms',
                  'djpcms.plugins.text',
                  'djpcms.plugins.snippet',
                  'sitedjpcms']

# djpcms settings
DEFAULT_TEMPLATE_NAME = 'base.html'
CONTENT_INLINE_EDITING = {'available':      True,
                          'pagecontent':    '/site-content/',
                          'width':          600,
                          'height':         500}
import djpcmsconfig
