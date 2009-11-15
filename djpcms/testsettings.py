import os

BASE = os.path.abspath(os.path.dirname(__file__))

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME   = '/tmp/djpcms.db'
INSTALLED_APPS  = ['django.contrib.contenttypes',
                   'tagging',
                   'djpcms']

# Silence logging
import logging

class Silence(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("djpcms").addHandler(Silence())


APPLICATION_MODULE = 'djpcms.tests.test_urls'