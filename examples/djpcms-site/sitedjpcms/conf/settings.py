DEBUG = True
TEMPLATE_DEBUG = DEBUG
SERVE_STATIC_FILES = DEBUG
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
    'openid_consumer.middleware.OpenIDMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'djpcms.permissions.Backend',
    'socialauth.auth_backends.OpenIdBackend',
    'socialauth.auth_backends.TwitterBackend',
    'socialauth.auth_backends.FacebookBackend',
    'socialauth.auth_backends.LinkedInBackend',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    #
    'djpcms',
    'djpcms.contrib.jdep',
    #'flowrepo',
    #'tagging',
    'socialauth',
    'openid_consumer',
    'south',
    'django.contrib.admin',
)


# The settings changed by the application
#==========================================================
import os
basedir = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
ROOT_URLCONF = 'sitedjpcms.urls'
APPLICATION_URL_MODULE = 'sitedjpcms.appurls'
TEMPLATE_DIRS = (os.path.join(basedir,'templates'),)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(basedir, 'media')
DJPCMS_STYLE = 'smooth'
TEMPLATE_CONTEXT_PROCESSORS = (
            "socialauth.context_processors.facebook_api_key",
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.contrib.messages.context_processors.messages",
            "djpcms.core.context_processors.djpcms"
            )
DJPCMS_PLUGINS = ['djpcms.plugins.*']
#DJPCMS_PLUGINS = ['djpcms.plugins.*',
#                  'flowrepo.cms.plugins']
DJPCMS_USER_CAN_EDIT_PAGES = True
#=========================================================
FLOWREPO_STORAGE_IMAGE      = 'sitedjpcms.storage.SiteFileSystemStorage'

