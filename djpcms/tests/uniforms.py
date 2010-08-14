import datetime

from django.test import TestCase

from djpcms.conf import settings
from djpcms.utils import uniforms


class Uniform(TestCase):
    
    def testSimple(self):
        class testform(uniforms.Form):
            name = uniforms.CharField()
        f = testform()