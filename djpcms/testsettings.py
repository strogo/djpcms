#
# Used by testing.py on the package directory for testing
#
import os
BASE = os.path.split(os.path.abspath(__file__))[0]
SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE,'tests','testdjpcms.sqlite')
    }
}


INSTALLED_APPS  = ['django.contrib.auth',
                   'django.contrib.sessions',
                   'django.contrib.sites',
                   'django.contrib.contenttypes',
                   'django.contrib.admin',
                   'djpcms',
                   'djpcms.contrib.jdep',
                   'djpcms.tests.testmodel']

#try:
#    import south
#    INSTALLED_APPS.append('south')
#except:
#    pass

TEMPLATE_DIRS     = os.path.join(BASE, 'tests', 'templates'),
ADMIN_MEDIA_PREFIX = '/media/admin/'
MEDIA_ROOT = os.path.join(BASE, 'tests', 'media')

# Silence logging
import logging

class Silence(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("djpcms").addHandler(Silence())

ROOT_URLCONF           = 'djpcms.tests.conf.urls'
APPLICATION_URL_MODULE = 'djpcms.tests.conf.test_urls'

TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.contrib.messages.context_processors.messages",
            "djpcms.core.context_processors.djpcms"
            )