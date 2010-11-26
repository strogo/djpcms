import random

from djpcms.test import TestCase
from djpcms.views import appsite, appview


def randomnumber(djp):
    return "New random number: {0}".format(random.uniform(0,1))

class RandomApplication(appsite.Application):
    home = appview.View(isapp = True, in_navigation = True, renderer = randomnumber)
    
appurls = RandomApplication('/apps/nodb/', name = 'random application'),


class TestBaseApplication(TestCase):
    '''Test an application without a database model.'''
    appurls = 'regression.appnodb.tests'
    
    def testPage(self):
        self.makepage(bit = 'apps')
        self.assertEqual(self.Page.objects.all().count(),2)
        context = self.get('/apps/nodb/')
        page = context['page']
        self.assertEqual(page,None)
        self.makepage('random_application-home')
        context = self.get('/apps/nodb/')
        page = context['page']
        self.assertTrue(page)
        self.assertTrue(page.parent.url,'/')
        
    def testNavigation(self):
        self.makepage(bit = 'apps')
        self.assertEqual(self.Page.objects.all().count(),2)
        context = self.get('/apps/nodb/')
        page = context['page']
        self.assertEqual(page,None)
        self.makepage('random_application-home')
        context = self.get('/')
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),1)
        sitenav = list(sitenav[0])
        self.assertEqual(len(sitenav),1)
        self.assertEqual(sitenav[0].url,'/apps/nodb/')
        
    def testContent(self):
        resp = self.get('/apps/nodb/', response = True)
        self.assertTrue("New random number: " in resp.content)
        
    