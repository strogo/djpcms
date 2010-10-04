from django import test
from django.contrib.auth.models import User

from djpcms.forms import model_to_dict
from djpcms.views.cache import pagecache
from djpcms.views import appsite
from djpcms.models import Page
from djpcms.forms import PageForm


class TestCase(test.TestCase):
    '''Implements shurtcuts function for testing djpcms'''
    
    def setUp(self):
        self.pagecache = pagecache
        self.Page = Page
        self.site = appsite.site
        self.clear()
        self.superuser = User.objects.create_superuser('testuser', 'test@testuser.com', 'testuser')
        self.user = User.objects.create_user('simpleuser', 'simple@testuser.com', 'simpleuser')
        
    def clear(self):
        self.pagecache.clear()
        return self.get()['page']
        
    def get(self, url = '/', status = 200):
        '''Quick function for getting some content'''
        response = self.client.get(url)
        self.assertEqual(response.status_code,status)
        return response.context
    
    def makepage(self, view = None, model = None, bit = '', parent = None, fail = False, **kwargs):
        form = PageForm()
        data = model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
        data.update(**kwargs)
        data.update({'url_pattern': bit,
                     'parent': None if not parent else parent.id})
        if model and view:
            appmodel = self.site.for_model(model)
            view = appmodel.getview(view)
            data['application'] = view.code
        form = PageForm(data = data)
        if fail:
            self.assertFalse(form.is_valid())
        else:
            self.assertTrue(form.is_valid())
            return form.save()
        
    def login(self, username = None, password = None):
        if not username:
            return self.client.login(username = 'testuser', password = 'testuser')
        else:
            return self.client.login(username = username,password = password)
        