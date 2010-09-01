from djpcms.testsettings import *

BASE  = os.path.split(os.path.abspath(__file__))[0]
DEBUG = True
DATABASE_NAME = os.path.join(BASE,'djpcmstest.sqlite')

INSTALLED_APPS += ('django.contrib.admin',)