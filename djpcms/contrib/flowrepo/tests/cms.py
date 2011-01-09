from djpcms.test import TestCase
from djpcms.contrib.flowrepo.models import Report, FlowItem
from djpcms.contrib.flowrepo.cms import NiceReportForm

__all__ = ['CmsTest']


class CmsTest(TestCase):
    appurls = 'djpcms.contrib.flowrepo.tests.appurls'
    
    def setUp(self):
        super(CmsTest,self).setUp()
        self.clear(True)
        self.makepage('main',FlowItem)
    
    def addReport(self,
                  title='Just a test',
                  abstract='This is a test report',
                  body='Empty',
                  tags='bla test'):
        self.assertTrue(self.login())
        uni = self.get('/weblog/add/')['uniform']
        data = uni.htmldata()
        data['title'] = title
        data['abstract'] = abstract
        data['body'] = body
        data['tags'] = tags
        self.post('/weblog/add/', data = data, status = 302)
        item = FlowItem.objects.latest()
        self.assertEqual(item.tags,tags)
        r = item.object
        self.assertEqual(r.name,title)
        self.assertEqual(r.description,abstract)
        self.assertEqual(r.body,body)
        return item
        
    def testRoot(self):
        context = self.get()
        page = context['page']
        djp  = context['djp']
        self.assertEqual(djp.url,'/')
        self.assertEqual(page,djp.page)
        self.assertEqual(page.url,'/')
        self.assertEqual(page.application_view,'flowitemapplication-main')
        
    def testAddReportForm(self):
        self.assertTrue(self.login())
        resp = self.get('/weblog/add/', response = True)
        context = resp.context
        uni = context['uniform']
        self.assertEqual(uni.instance.__class__,FlowItem)
        self.assertEqual(uni.template,'flowrepo/report-form.html')
        forms = list(uni.forms_only())
        self.assertEqual(len(forms),1)
        form = forms[0]
        self.assertEqual(form.__class__,NiceReportForm)
        layout = form.layout
        self.assertEqual(layout.template,'flowrepo/report-form-layout.html')
        
    def testAddReportResponse(self):
        self.addReport()
        
    def testEditReportForm(self):
        item = self.addReport()
        resp = self.get('/weblog/{0}/edit/'.format(item.object.slug), response = True)
        context = resp.context
        uni = context['uniform']
        self.assertEqual(uni.instance.__class__,FlowItem)
        self.assertEqual(uni.template,'flowrepo/report-form.html')
        forms = list(uni.forms_only())
        self.assertEqual(len(forms),1)
        form = forms[0]
        self.assertEqual(form.__class__,NiceReportForm)
        layout = form.layout
        self.assertEqual(layout.template,'flowrepo/report-form-layout.html')
        
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
        
    
    