#
# Used by testing.py on the package directory for testing
#
import os
BASE = os.path.split(os.path.abspath(__file__))[0]
SITE_ID = 1
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME   = '/tmp/testdjpcms.db'


INSTALLED_APPS  = ['django.contrib.auth',
                   'django.contrib.sessions',
                   'django.contrib.sites',
                   'django.contrib.contenttypes',
                   'djpcms']


TEMPLATE_DIRS     = os.path.join(BASE, 'templates','djpcms','tests'),


# Silence logging
import logging

class Silence(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("djpcms").addHandler(Silence())

ROOT_URLCONF           = 'djpcms.tests.urls'
APPLICATION_URL_MODULE = 'djpcms.tests.test_urls'