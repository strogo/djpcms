from django.contrib.auth.models import User

from djpcms.test import TestCase
from djpcms.contrib.flowrepo.models import Report, FlowItem

__all__ = ['CmsTest']


class CmsTest(TestCase):
    appurls = 'djpcms.contrib.flowrepo.tests.appurls'
    
    def setUp(self):
        super(CmsTest,self).setUp()
        self.Page.objects.all().delete()
        self.makepage('main',FlowItem)
        
    def testRoot(self):
        context = self.get()
        page = context['page']
        djp  = context['djp']
        self.assertEqual(djp.url,'/')
        self.assertEqual(page,djp.page)
        self.assertEqual(page.url,'/')
        self.assertEqual(page.application_view,'flowitemapplication-main')
        
        
    def testContent(self):
        djp = self.get()['djp']
        p0  = djp.page
        children = djp.children
        self.assertEqual(len(children),0)
        #
        # Add a page for weblog
        p1 = self.makepage('applications',FlowItem)
        p2 = self.makepage('applications',FlowItem,'weblog')
        self.assertNotEqual(p1,p2)
        self.assertEqual(p1.parent,p0)
        self.assertEqual(p2.parent,p0)
        
        djp = self.get()['djp']
        children = djp.children
        self.assertEqual(len(children),1)
        child = children[0]
        self.assertEqual(child.url,'/weblog/')
        #self.assertEqual(str(child),'example.com/write/')
        
    def testUpload(self):
        self.login()
        context = self.get('/upload/')
        
    