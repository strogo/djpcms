import datetime

from django.test import TestCase
from django.conf import settings
from djpcms.contrib.jdep.fabtools import *


class Deployment(TestCase):
    
    def setUp(self):
        env.host_string = 'localhost'
        a = 1
    
    def testPythonVersion(self):
        pass
        