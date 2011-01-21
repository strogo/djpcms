import json
import unittest
import signal

import djpcms
from djpcms import sites, get_site
from djpcms.utils.importer import import_module
from djpcms.plugins import SimpleWrap
from djpcms.forms import fill_form_data, model_to_dict, cms
from djpcms.models import Page
from djpcms.apps.included.user import UserClass
from djpcms.core.exceptions import *

from django import test
from django.db.models import get_app, get_apps

from BeautifulSoup import BeautifulSoup


class DjpCmsTestHandle(test.TestCase):
    '''Implements shortcut functions for testing djpcms.
Must be used as a base class for TestCase classes'''
    urlbase   = '/'
    Page = Page
    sites = sites
    
    def _pre_setup(self):
        sites.settings.TESTING = True
        super(DjpCmsTestHandle,self)._pre_setup()
        
    def _urlconf_setup(self):
        sites.clear()
        sett = sites.settings
        appurls = getattr(self,'appurls',None)
        self.site = sites.make(sett.SITE_DIRECTORY,
                               'conf',
                               route = self.urlbase,
                               APPLICATION_URL_MODULE = appurls)
        self.settings = self.site.settings
        sites.load()
            
    def _urlconf_teardown(self):
        sites.clear()
        super(DjpCmsTestHandle,self)._urlconf_teardown()
    
    def clear(self, db = False):
        '''If db is set to True it clears the database pages'''
        if db:
            self.Page.objects.all().delete()
        else:
            sites.clear()

    def makepage(self, view = None, model = None, bit = '', parent = None, fail = False, **kwargs):
        form = cms.PageForm()
        data = model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
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
        
        
class TestCase(DjpCmsTestHandle):
        
    def setUp(self):
        p = self.get()['page']
        self.superuser = UserClass().create_super('testuser', 'test@testuser.com', 'testuser')
        self.user = UserClass().create('simpleuser', 'simple@testuser.com', 'simpleuser')
        self.assertEqual(p.url,'/')
        #if not hasattr(self,'fixtures'):
        #    self.assertEqual(Page.objects.all().count(),1)
            
    def editurl(self, url):
        return '/{0}{1}'.format(self.site.settings.CONTENT_INLINE_EDITING['preurl'],url)
        
    def login(self, username = None, password = None):
        if not username:
            return self.client.login(username = 'testuser', password = 'testuser')
        else:
            return self.client.login(username = username,password = password)
        
    
class PluginTest(TestCase):
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
    