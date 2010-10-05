import datetime

from djpcms.test import TestCase
from djpcms.conf import settings
from djpcms.utils import navigation

from testmodel.models import Strategy


class TestSiteNavigation(TestCase):
    fixtures = ["test.json"]
        
    def testMainNavigation(self):
        context = self.get()
        sitenav = context["sitenav"]
        self.assertTrue(isinstance(sitenav,navigation.Navigator))
        for item in sitenav:
            url = item.url
            self.assertTrue(len(url)>2)
            self.assertTrue(url.startswith('/'))
            self.assertTrue(url.endswith('/'))
        N = len(sitenav)
        pages1 = list(self.Page.objects.filter(level = 1, in_navigation__gt = 0))
        self.assertEqual(N,len(pages1))
        
        

class TestApplicationNavigation(TestCase):
    
    def testSimpleApplication(self):
        p0 = self.makepage(bit = 'random')
        p1 = self.makepage('search', Strategy, in_navigation = 5)
        p2 = self.makepage('add',Strategy)
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),2)
        self.assertEqual(sitenav[0].url,'/random/')
        self.assertEqual(sitenav[1].url,'/strategies/')
        snav = list(sitenav[1])
        self.assertEqual(len(snav),0)
        #
        # now lets login
        self.assertTrue(self.login())
        context = self.get()
        snav = list(list(context["sitenav"])[1])
        self.assertEqual(len(snav),1)
        self.assertEqual(snav[0].url,'/strategies/add/')
        
    def testApplicationWithMultiPage(self):
        '''We create some specialised pages for some Strategy objects and
check that they appear in navigation.'''
        Strategy(name='the good').save()
        Strategy(name='the bad').save()
        Strategy(name='the ugly').save()
        ps = self.makepage('search', Strategy)
        p0 = self.makepage('view', Strategy)
        p1 = self.makepage('view', Strategy, bit='1', in_navigation = 2)
        p2 = self.makepage('view', Strategy, bit='2', in_navigation = 1)
        self.assertNotEqual(p1,p0)
        self.assertNotEqual(p2,p1)
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),1)     
        self.assertEqual(sitenav[0].url,'/strategies/')
        snav = list(sitenav[0])
        self.assertEqual(len(snav),2)
        #
        context = self.get('/strategies/')
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),1)  
        self.assertEqual(sitenav[0].url,'/strategies/')
        snav = list(sitenav[0])
        self.assertEqual(len(snav),2)
        #
        context = self.get('/strategies/3/')
        self.assertEqual(context['page'],p0)
        context = self.get('/strategies/1/')
        self.assertEqual(context['page'],p1)
        context = self.get('/strategies/2/')
        self.assertEqual(context['page'],p2)
        


class TestRootApplicationNavigation(TestCase):
    
    def setUp(self):
        Strategy(name = 'one').save()
        Strategy(name = 'two').save()
        Strategy(name = 'three').save()
        Strategy(name = 'four').save()
        super(TestRootApplicationNavigation,self).setUp()
        self.Page.objects.all().delete()
        app = self.site.unregister(Strategy)
        self.site.register('/',app,model = Strategy)
        p = self.makepage('search',Strategy)
        p0 = self.makepage(bit = 'random')
        self.assertFalse(p0.application)
        self.assertEqual(p,p0.parent)
        self.assertTrue(p.application)
        self.assertEqual(p.url,'/')
        
    def testSimpleApplication(self):
        p1 = self.makepage('add',Strategy,in_navigation=2)
        self.login()
        context = self.get()
        p = context['page']
        self.assertTrue(p.application)
        self.assertTrue(p1.application)
        self.assertEqual(p,p1.parent)
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),2)
        self.assertEqual(sitenav[0].url,'/random/')
        self.assertEqual(sitenav[1].url,'/add/')
    
    def testMultiPageApplication(self):
        s0 = self.makepage('view',Strategy)
        s1 = self.makepage('view',Strategy,'1',in_navigation=3)
        s2 = self.makepage('view',Strategy,'2',in_navigation=2)
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),3)
        self.assertEqual(sitenav[1].url,'/2/')
        self.assertEqual(sitenav[2].url,'/1/')
        
        for i in range(1,5):
            context = self.get('/%s/' % i)
            sitenav = list(context["sitenav"])
            self.assertEqual(len(sitenav),3)
            self.assertEqual(sitenav[1].url,'/2/')
            self.assertEqual(sitenav[2].url,'/1/')
            
    def testMultiPageApplicationWithChildren(self):
        s0 = self.makepage('view',Strategy)
        s1 = self.makepage('view',Strategy,'1',in_navigation=3)
        s2 = self.makepage('view',Strategy,'2',in_navigation=2)
        a  = self.makepage('edit',Strategy)
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),3)
        self.assertEqual(sitenav[1].url,'/2/')
        self.assertEqual(sitenav[2].url,'/1/')
        self.assertFalse(list(sitenav[1]))
        self.assertFalse(list(sitenav[2]))
        
    def testMultiPageApplicationWithSpecialChildren(self):
        s0 = self.makepage('view',Strategy)
        s1 = self.makepage('view',Strategy,'1',in_navigation=3)
        s2 = self.makepage('view',Strategy,'2',in_navigation=2)
        a  = self.makepage('edit',Strategy)
        a1 = self.makepage('edit',Strategy, parent = s1, in_navigation = 10)
        self.login()
        context = self.get()
        sitenav = list(context["sitenav"])
        self.assertEqual(len(sitenav),3)
        self.assertEqual(sitenav[1].url,'/2/')
        self.assertEqual(sitenav[2].url,'/1/')
        self.assertFalse(list(sitenav[1]))
        nav = list(sitenav[2])
        self.assertEqual(len(nav),1)
        
        
    def tearDown(self):
        app = self.site.unregister(Strategy)
        self.site.register('/strategies/',app,model = Strategy)
    