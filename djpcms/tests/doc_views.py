import datetime

from django.test import TestCase
from django.conf import settings


class DocsViewTest(TestCase):
    fixtures = ["test.json"]
    
    def callView(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        if isinstance(response.context, list):
            return response.context[1]
        else:
            return response.context
        
    def testIndex(self):
        context = self.callView('/docs/')
        pass
        #pa = context["paginator"]