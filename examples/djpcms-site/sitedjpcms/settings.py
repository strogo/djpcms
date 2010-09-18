from localsettings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Luca Sbardella', 'luca.sbardella@gmail.com'),
)

MANAGERS = ADMINS
TIME_ZONE     = 'Europe/London'
LANGUAGE_CODE = 'en-uk'
SITE_ID = 1
USE_I18N = False
USE_L10N = True
SECRET_KEY = 'vctw)*^2z!1fzie12zzdxf45)-rc(^7qvd(vabn&1&ogwehidr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #
    'djpcms',
    'djpcms.contrib.admin',
    'socialauth',
    'openid_consumer',
    #'django.contrib.admin',
)


# The settings changed by the application
#==========================================================
import os
basedir = os.path.split(os.path.abspath(__file__))[0]
ROOT_URLCONF = 'sitedjpcms.urls'
APPLICATION_URL_MODULE = 'sitedjpcms.appurls'
TEMPLATE_DIRS = (os.path.join(basedir,'templates'),)
ADMIN_MEDIA_PREFIX = '/media/admin/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(basedir, 'media')
DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': os.path.join(basedir,'sitedjpcms.sqlite'),
    }
}
DJPCMS_STYLE = 'green'
TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.contrib.messages.context_processors.messages",
            "djpcms.core.context_processors.djpcms"
            )
#=========================================================
