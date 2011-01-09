import datetime

from djpcms.test import TestCase
from djpcms.utils import navigation

from regression.rootappnav.models import Strategy


class TestRootApplicationNavigation(TestCase):
    appurls = 'regression.rootappnav.appurls'
    
    def setUp(self):
        super(TestRootApplicationNavigation,self).setUp()
        self._init()
        
    def _init(self):
        self.Page.objects.all().delete()
        p0 = self.makepage('search',Strategy)
        Strategy(name = 'one').save()
        Strategy(name = 'two').save()
        Strategy(name = 'three').save()
        Strategy(name = 'four').save()
        p1 = self.makepage(bit = 'random')
        self.assertFalse(p1.application)
        self.assertEqual(p0,p1.parent)
        self.assertTrue(p0.application)
        self.assertEqual(p0.url,'/')
        
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
        
        # Loop over the 4 objects
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
        
    