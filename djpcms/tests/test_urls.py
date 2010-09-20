from django.test import TestCase
from django.conf import settings


class TestExtraUrls(TestCase):
    fixtures = ["test.json"]
    
    def testExtra(self):
        pass