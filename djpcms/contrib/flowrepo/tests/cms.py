from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.views import appsite
from djpcms.views.cache import pagecache
from djpcms.models import Page

from flowrepo.models import Report, FlowItem

__all__ = ['CmsTest']


class CmsTest(TestCase):
    
    def clear(self):
        page = super(CmsTest,self).clear()
        self.appmodel = self.site.for_model(FlowItem)
        page.application = self.appmodel.root_application.code
        page.save()
        
    def testRoot(self):
        context = self.get('/')
        page = context['page']
        self.assertTrue(page.url,'/')
        self.assertEqual(page.application,'flowitemapplication-main')
        
    def testContent(self):
        djp = self.get('/')['djp']
        self.assertTrue(djp.url,'/')
        children = djp.children
        self.assertEqual(len(children),0)
        #
        # Add a page for writing
        p1 = self.makepage('applications',FlowItem)
        p2 = self.makepage('applications',FlowItem,'writing')
        self.assertNotEqual(p1,p2)
        djp = self.get('/')['djp']
        children = djp.children
        self.assertEqual(len(children),1)
        child = children[0]
        self.assertEqual(child.url,'/writing/')
        #self.assertEqual(str(child),'example.com/write/')
        
    def testUpload(self):
        self.login()
        context = self.get('/upload/')
        
    