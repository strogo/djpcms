import datetime

from django.test import TestCase
from django.conf import settings

from djpcms.utils import navigation
from djpcms.models import Page


class TestSiteNavigation(TestCase):
    fixtures = ["test.json"]
    
    def callView(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)
        if isinstance(response.context, list):
            return response.context[1]
        else:
            return response.context
        
    def testMainNavigation(self):
        context = self.callView('/')
        sitenav = context["sitenav"]
        self.assertTrue(isinstance(sitenav,navigation.Navigator))
        for item in sitenav:
            url = item['url']
            self.assertTrue(len(url)>2)
            self.assertTrue(url.startswith('/'))
            self.assertTrue(url.endswith('/'))
        N = len(sitenav)
        pages1 = list(Page.objects.filter(level = 1, in_navigation__gt = 0))
        self.assertEqual(N,len(pages1))
            
    
    