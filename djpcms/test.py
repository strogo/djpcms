from django import test
from django.contrib.auth.models import User

from djpcms.forms import model_to_dict
from djpcms.views.cache import pagecache
from djpcms.views import appsite
from djpcms.models import Page
from djpcms.forms import PageForm


class TestCase(test.TestCase):
    
    def setUp(self):
        self.pagecache = pagecache
        self.Page = Page
        self.site = appsite.site
        self.clear()
        self.user = User.objects.create_user('testuser', 'test@testuser.com', 'testuser')
        
    def clear(self):
        self.pagecache.clear()
        self.get()
        
    def makepage(self, view, model, bit = '', fail = False):
        appmodel = self.site.for_model(model)
        view = appmodel.getview(view)
        form = PageForm()
        data = model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
        data.update({'application': view.code, 'url_pattern': bit})
        form = PageForm(data = data)
        if fail:
            self.assertFalse(form.is_valid())
        else:
            self.assertTrue(form.is_valid())
            return form.save()