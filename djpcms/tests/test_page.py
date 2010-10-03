from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.conf import settings

from testmodel.models import Strategy


class TestPage(TestCase):
        
    def get(self, url = '/', status = 200):
        response = self.client.get(url)
        self.assertEqual(response.status_code,status)
        return response.context
    
    def testRoot(self):
        context = self.get()
        page = context['page']
        self.assertEqual(page.url,'/')
        self.assertEqual(page.parent,None)
    
    def testApplication(self):
        context = self.get('/strategies/')
        page = context['page']
        self.assertEqual(page,None)
        self.makepage('search',Strategy)
        context = self.get('/strategies/')
        page = context['page']
        self.assertEqual(page.url,'/strategies/')
        self.assertEqual(page.parent,self.Page.objects.root_for_site())
        
    def testUrlPattern1(self):
        p = self.makepage('search',Strategy,'blabla')
        self.assertEqual(p.url_pattern,'')
        
    def testObjectView(self):
        Strategy(name = 'test').save()
        self.makepage('search',Strategy)
        self.makepage('view',Strategy)
        context = self.get('/strategies/1/')
        page = context['page']
        djp = context['djp']
        view = djp.view
        self.assertEqual(djp.page,page)
        
    def testObjectViewSpecial(self):
        Strategy(name = 'test1').save()
        Strategy(name = 'test2').save()
        sp = self.makepage('search',Strategy)
        sp = self.makepage('search',Strategy,'blabla',fail=True)
        vp = self.makepage('view',Strategy)
        vp1 = self.makepage('view',Strategy,'1')
        self.assertNotEqual(vp,vp1)
        self.assertEqual(vp.application,vp1.application)
        self.assertEqual(vp.parent,vp1.parent)
        self.assertFalse(vp.url_pattern)
        self.assertTrue(vp1.url_pattern)
        self.assertNotEqual(vp.url,vp1.url)
        context = self.get('/strategies/2/')
        page = context['page']
        djp  = context['djp']
        self.assertEqual(page,vp)
        context = self.get('/strategies/1/')
        page1 = context['page']
        self.assertEqual(page1,vp1)
        djp1 = context['djp']
        self.assertNotEqual(djp.view,djp1.view)
        self.assertEqual(djp.view.code,djp1.view.code)
        