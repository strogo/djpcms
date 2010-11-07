
from forms import *

try:
    from cms import *
except:
    pass



from django.test import TestCase

import flowrepo as me


class TestMe(TestCase):

    def test_version(self):
        self.assertTrue(me.VERSION)
        self.assertTrue(me.__version__)
        self.assertEqual(me.__version__,me.get_version())
        self.assertTrue(len(me.VERSION) >= 2)

    def test_meta(self):
        for m in ("__author__", "__contact__", "__homepage__", "__doc__"):
            self.assertTrue(getattr(me, m, None))