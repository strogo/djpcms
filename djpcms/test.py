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
from django.core.urlresolvers import clear_url_caches

from BeautifulSoup import BeautifulSoup


class TestEnvironment(object):
    '''Set up the test environment by checking which 3rd party
package is available'''

    def __init__(self, suite):
        sites.settings.DEBUG = False
        self.suite = suite
        self.libs = []
        self.check('django')
        self.check('werkzeug')
        self.check('sqlalchemy')
        self.setup()
        
    def check(self, name):
        try:
            import_module(name)
            self.libs.append(name)
        except ImportError:
            return None

    def setup(self):
        self._call('setup')
        
    def setupdb(self):
        self._call('setupdb')
        
    def teardown(self):
        self._call('teardown')
        
    def _call(self, funcname):
        for lib in self.libs:
            attname = '{0}_{1}'.format(funcname,lib)
            attr = getattr(self,attname,None)
            if attr:
                attr()
            
    def setup_django(self):
        from django.test.utils import setup_test_environment
        setup_test_environment()
        
    def setupdb_django(self):
        from django.db import connections
        old_names = []
        mirrors = []
        suite = self.suite
        for alias in connections:
            connection = connections[alias]
            # If the database is a test mirror, redirect it's connection
            # instead of creating a test database.
            if connection.settings_dict['TEST_MIRROR']:
                mirrors.append((alias, connection))
                mirror_alias = connection.settings_dict['TEST_MIRROR']
                connections._connections[alias] = connections[mirror_alias]
            else:
                old_names.append((connection, connection.settings_dict['NAME']))
                connection.creation.create_test_db(suite.verbosity, autoclobber=not suite.interactive)
        self.django_old_config = old_names, mirrors
        
    def teardown_django(self):
        from django.test.utils import teardown_test_environment
        from django.db import connections
        teardown_test_environment()
        suite = self.suite
        old_names, mirrors = self.django_old_config
        # Point all the mirrors back to the originals
        for alias, connection in mirrors:
            connections._connections[alias] = connection
        # Destroy all the non-mirror databases
        for connection, old_name in old_names:
            connection.creation.destroy_test_db(old_name, suite.verbosity)
        
        
def build_suite(app_module):
    '''Create a test suite for the provided application module.
Look into the test module if it exists otherwise do nothing.'''
    suite = unittest.TestSuite()
    app_path = app_module.__name__.split('.')[:-1] 
    try:
        test_module = import_module('{0}.tests'.format('.'.join(app_path)))
    except ImportError:
        test_module = None
    if test_module:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_module))
    return suite
        

class DjpcmsTestRunner(unittest.TextTestRunner):
    '''Test runner adapted from django'''
    def __init__(self, verbosity=0, failfast=False, **kwargs):
        super(DjpcmsTestRunner, self).__init__(verbosity=verbosity, **kwargs)
        self.failfast = failfast
        self._keyboard_interrupt_intercepted = False

    def run(self, *args, **kwargs):
        """
        Runs the test suite after registering a custom signal handler
        that triggers a graceful exit when Ctrl-C is pressed.
        """
        self._default_keyboard_interrupt_handler = signal.signal(signal.SIGINT,
            self._keyboard_interrupt_handler)
        try:
            result = super(DjpcmsTestRunner, self).run(*args, **kwargs)
        finally:
            signal.signal(signal.SIGINT, self._default_keyboard_interrupt_handler)
        return result

    def _keyboard_interrupt_handler(self, signal_number, stack_frame):
        """
        Handles Ctrl-C by setting a flag that will stop the test run when
        the currently running test completes.
        """
        self._keyboard_interrupt_intercepted = True
        sys.stderr.write(" <Test run halted by Ctrl-C> ")
        # Set the interrupt handler back to the default handler, so that
        # another Ctrl-C press will trigger immediate exit.
        signal.signal(signal.SIGINT, self._default_keyboard_interrupt_handler)

    def _makeResult(self):
        result = super(DjpcmsTestRunner, self)._makeResult()
        failfast = self.failfast

        def stoptest_override(func):
            def stoptest(test):
                # If we were set to failfast and the unit test failed,
                # or if the user has typed Ctrl-C, report and quit
                if (failfast and not result.wasSuccessful()) or \
                    self._keyboard_interrupt_intercepted:
                    result.stop()
                func(test)
            return stoptest

        setattr(result, 'stopTest', stoptest_override(result.stopTest))
        return result


class DjpcmsTestSuiteRunner(object):
    
    def __init__(self, verbosity=1, interactive=True, failfast=True, **kwargs):
        self.verbosity = verbosity
        self.interactive = interactive
        self.failfast = failfast

    def setup_test_environment(self, **kwargs):
        self.environment = TestEnvironment(self)
        return self.environment

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return suite

    def run_suite(self, suite, **kwargs):
        return DjpcmsTestRunner(verbosity=self.verbosity, failfast=self.failfast).run(suite)

    def teardown_databases(self, old_config, **kwargs):
        from django.db import connections
        old_names, mirrors = old_config
        # Point all the mirrors back to the originals
        for alias, connection in mirrors:
            connections._connections[alias] = connection
        # Destroy all the non-mirror databases
        for connection, old_name in old_names:
            connection.creation.destroy_test_db(old_name, self.verbosity)

    def suite_result(self, suite, result, **kwargs):
        return len(result.failures) + len(result.errors)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """
        Run the unit tests for all the test labels in the provided list.
        Labels must be of the form:
         - app.TestClass.test_method
            Run a single specific test method
         - app.TestClass
            Run all the test methods in a given class
         - app
            Search for doctests and unittests in the named application.

        When looking for tests, the test runner will look in the models and
        tests modules for the application.

        A list of 'extra' tests may also be provided; these tests
        will be added to the test suite.

        Returns the number of tests that failed.
        """
        env = self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        env.setupdb()
        result = self.run_suite(suite)
        env.teardown()
        return self.suite_result(suite, result)
    
    
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
        appurls = getattr(self,'appurls',None)
        settings = sites.settings
        self._old_appurl = settings.APPLICATION_URL_MODULE
        settings.APPLICATION_URL_MODULE = appurls
        self.site = self.CreateSites()
        
    def CreateSites(self):
        sett = sites.settings
        sites.make(sett.SITE_DIRECTORY,'conf')
        site = sites.get_site(self.urlbase)
        sites.load() # load the site
        return site
            
    def _urlconf_teardown(self):
        sites.settings.APPLICATION_URL_MODULE = self._old_appurl
        sites.clear()
        super(DjpCmsTestHandle,self)._urlconf_teardown()
    
    def clear(self, db = False):
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
        c = self._simplePage()
        self.assertTrue(self.login())
        ec = self.get(self.editurl('/'))
        self.assertEqual(c['page'],ec['page'])
        inner = ec['inner']
        bs = self.bs(inner).find('div', {'id': 'blockcontent-1-0-0'})
        self.assertTrue(bs)
        f  = bs.find('form')
        self.assertTrue(f)
        action = dict(f.attrs)['action']
        
        # Send bad post request
        res = self.post(action, {}, ajax = True, response = True)
        self.assertEqual(res['content-type'],'application/javascript')
        body = json.loads(res.content)
        self.assertFalse(body['error'])
        self.assertEqual(body['header'],'htmls')
        
        data = {'plugin_name': self.plugin.name,
                'container_type': SimpleWrap.name}
        data.update(self.get_plugindata(f))
        res = self.post(action, data, ajax = True, response = True)
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
    