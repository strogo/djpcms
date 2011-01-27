import json
import unittest

import djpcms
from djpcms import sites, forms
from djpcms.forms.utils import fill_form_data
from djpcms.core.exceptions import *

from BeautifulSoup import BeautifulSoup

#from .client import Client


class TestCase(unittest.TestCase):
    '''Implements shortcut functions for testing djpcms.
Must be used as a base class for TestCase classes'''
    #client_class = Client
    urlbase   = '/'
    sites = sites
    _env = None
    
    def _pre_setup(self):
        from djpcms.core import api
        self.api = api
        sites.settings.TESTING = True
        self.site = self.makesite()
        if self.site:
            self.settings = self.site.settings
            sites.load()
        if self._env:
            self._env.pre_setup()
        
    def makesite(self):
        '''Setup the site'''
        appurls = getattr(self,'appurls',None)
        self.sites.clear()
        sett = sites.settings
        return sites.make(sett.SITE_DIRECTORY,
                          'conf',
                          route = self.urlbase,
                          APPLICATION_URL_MODULE = appurls)
        
    def __call__(self, result=None):
        """
        Wrapper around default __call__ method to perform common Django test
        set up. This means that user-defined Test Cases aren't required to
        include a call to super().setUp().
        """
        #self.client = self.client_class()
        from .client import Client
        self.client = Client()
        self._pre_setup()
        super(TestCase, self).__call__(result)
        self._post_teardown()
            
    def _post_teardown(self):
        if self._env:
            self._env.post_teardown()
    
    def clear(self, db = False):
        '''If db is set to True it clears the database pages'''
        if db:
            self.api.all().delete()
        else:
            sites.clear()

    def makepage(self, view = None, model = None, bit = '', parent = None, fail = False, **kwargs):
        create_page = self.api.create_page
        if fail:
            self.assertRaises(forms.ValidationError, create_page)
        else:
            page = create_page()
            self.assertTrue(page.pk)
            return page
        #data = model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
        data = {}
        data.update(**kwargs)
        data.update({'url_pattern': bit,
                     'parent': None if not parent else parent.id})
        if view:
            if model:
                appmodel = self.site.for_model(model)
                view = appmodel.getview(view)
            else:
                view = self.site.getapp(view)
            data['application_view'] = view.code
        form = cms.PageForm(data = data)
        if fail:
            self.assertFalse(form.is_valid())
        else:
            self.assertTrue(form.is_valid())
            instance = form.save()
            self.assertTrue(instance.pk)
            return instance

    def post(self, url = '/', data = {}, status = 200,
             response = False, ajax = False):
        '''Quick function for posting some content'''
        if ajax:
            resp = self.client.post(url,data,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            resp = self.client.post(url,data)
        self.assertEqual(resp.status_code,status)
        if response:
            return resp
        else:
            return resp.context
    
    def get(self, url = '/', status = 200, response = False,
            ajax = False):
        '''Quick function for getting some content'''
        if ajax:
            resp = self.client.get(url,HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        else:
            resp = self.client.get(url)
        self.assertEqual(resp.status_code,status)
        if response:
            return resp
        else:
            return resp.context
        
    def bs(self, doc):
        return BeautifulSoup(doc)
        
        
class TestCaseWithUser(TestCase):
        
    def _pre_setup(self):
        super(TestCaseWithUser,self)._pre_setup()
        p = self.get()['page']
        self.assertEqual(p.url,'/')
        User = self.site.User
        if User:
            self.superuser = User.create_super('testuser', 'test@testuser.com', 'testuser')
            self.user = User.create('simpleuser', 'simple@testuser.com', 'simpleuser')
        else:
            self.superuser = None
            self.user = None
            
    def editurl(self, url):
        return '/{0}{1}'.format(self.site.settings.CONTENT_INLINE_EDITING['preurl'],url)
        
    def login(self, username = None, password = None):
        if not username:
            return self.client.login(username = 'testuser', password = 'testuser')
        else:
            return self.client.login(username = username,password = password)
        
    
class PluginTest(TestCaseWithUser):
    plugin = None
    
    def _pre_setup(self):
        super(PluginTest,self)._pre_setup()
        module = self.plugin.__module__
        self.site.settings.DJPCMS_PLUGINS = [module]
        
    def _simplePage(self):
        c = self.get('/')
        p = c['page']
        p.set_template(p.create_template('simple','{{ content0 }}','content'))
        b = p.add_plugin(self.plugin)
        self.assertEqual(b.plugin_name,self.plugin.name)
        self.assertEqual(b.plugin,self.plugin())
        return c
        
    def request(self, user = None):
        req = sites.http.HttpRequest()
        req.user = user
        return req
        
    def testBlockOutOfBound(self):
        p = self.get('/')['page']
        self.assertRaises(BlockOutOfBound, p.add_plugin, self.plugin)
        
    def testSimple(self):
        self._simplePage()
    
    def testEdit(self):
        from djpcms.plugins import SimpleWrap
        '''Test the editing view by getting a the view and the editing form
and sending AJAX requests.'''
        c = self._simplePage()
        # we need to login to perform editing
        self.assertTrue(self.login())
        # get the editing page for '/'
        ec = self.get(self.editurl('/'))
        # '/' and editing page '/' are the same
        self.assertEqual(c['page'],ec['page'])
        # inner editing page
        inner = ec['inner']
        # beautiful soup the block content
        bs = self.bs(inner).find('div', {'id': 'blockcontent-1-0-0'})
        self.assertTrue(bs)
        f  = bs.find('form')
        self.assertTrue(f)
        action = dict(f.attrs)['action']
        # get the prefix
        prefix = bs.find('input', attrs = {'name':'_prefixed'})
        self.assertTrue(prefix)
        prefix = dict(prefix.attrs)['value']
        self.assertTrue(prefix)
        
        # Send bad post request (no data)
        res = self.post(action, {}, ajax = True, response = True)
        self.assertEqual(res['content-type'],'application/javascript')
        body = json.loads(res.content)
        self.assertFalse(body['error'])
        self.assertEqual(body['header'],'htmls')
        
        for msg in body['body']:
            if msg['identifier'] != '.form-messages':
                self.assertEqual(msg['html'][:26],'<ul class="errorlist"><li>')
        
        data = {'plugin_name': self.plugin.name,
                'container_type': SimpleWrap.name}
        data.update(self.get_plugindata(f))
        pdata = dict(((prefix+'-'+k,v) for k,v in data.items()))
        pdata['_prefixed'] = prefix
        res = self.post(action, pdata, ajax = True, response = True)
        self.assertEqual(res['content-type'],'application/javascript')
        body = json.loads(res.content)
        self.assertFalse(body['error'])
        
        preview = False
        for msg in body['body']:
            if msg['identifier'] == '#plugin-1-0-0-preview':
                html = msg['html']
                preview = True
                break
        self.assertTrue(preview)
        
    def testRender(self):
        self.testEdit()
        c = self.get('/')
        inner = c['inner']
        bs = self.bs(inner).find('div', {'class': 'djpcms-block-element plugin-{0}'.format(self.plugin.name)})
        self.assertTrue(bs)
        return bs
    
    def get_plugindata(self, soup_form, request = None):
        '''To be implemented by derived classes'''
        form = self.plugin.form
        return fill_form_data(form(request = request)) if form else {}
    