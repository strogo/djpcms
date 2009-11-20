import os

SERVE_STATIC_FILES = True
DEBUG = True
TEMPLATE_DEBUG = DEBUG


import packages
PSETTINGS = packages.install(DEBUG)

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE   = PSETTINGS.dbengine
DATABASE_NAME     = PSETTINGS.dbname
DATABASE_USER     = PSETTINGS.dbuser
DATABASE_PASSWORD = PSETTINGS.dbpassword
DATABASE_HOST     = PSETTINGS.dbhost
DATABASE_PORT     = PSETTINGS.dbport

SECRET_KEY = '9ydnib90%5_reb+*klqo5*y&kozxxp(mdyc(7uqrifa*=(ln$3'
TIME_ZONE             = 'Europe/London'
LANGUAGE_CODE         = 'en-gb'
SITE_ID = 1
USE_I18N = False

DATE_FORMAT            = 'D d M y'
DATETIME_FORMAT        = 'D d M y P'
SERVE_STATIC_FILES     = PSETTINGS.servs
MEDIA_ROOT             = PSETTINGS.media_root()
MEDIA_URL              = '/media/'
ADMIN_MEDIA_PREFIX     = MEDIA_URL + 'django_admin/'
SECRET_KEY             = PSETTINGS.id.SECRET_KEY
ADMIN_URL_PREFIX       = PSETTINGS.id.ADMIN_URL_PREFIX
 
USER_ACCOUNT_HOME_URL  = '/accounts/'
LOGIN_URL  = '%slogin/' % USER_ACCOUNT_HOME_URL
LOGOUT_URL = '%slogout/' % USER_ACCOUNT_HOME_URL


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

TEMPLATE_DIRS     = (os.path.join(PSETTINGS.LOCDIR, 'templates'))

INSTALLED_APPS = ['django.contrib.auth',
                  'django.contrib.sites',
                  'django.contrib.contenttypes',
                  'django.contrib.sessions',
                  #'django.contrib.admin',
                  'djpcms']

# djpcms settings
DEFAULT_TEMPLATE_NAME = 'base.html'
CONTENT_INLINE_EDITING = {'available':      True,
                          'pagecontent':    '/site-content/',
                          'width':          600,
                          'height':         500}
APPLICATION_MODULE     = 'sitedjpcms.appurls'
import djpcms.utils.markups.install
