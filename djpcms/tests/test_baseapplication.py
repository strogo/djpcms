from djpcms.test import TestCase
from djpcms.conf import settings


class TestBaseApplication(TestCase):
    '''Test an application without a database model'''
    
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
    