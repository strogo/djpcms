from django.contrib.auth.models import User

from djpcms.models import SiteConfiguration
from forms import RegisterForm
from tools import *



class adduserform(form):
    '''
    A search form plugin.
    This plugin display a serch widget a-la google
    '''
    def __init__(self, **attrs):
        super(adduserform,self).__init__(**attrs)
        
    def _createform(self, data = None, **kwargs):
        co = self.make_container(div, cn = self.classes.search_entry)
        co['add']  = formlet(form     = self.view._form,
                             data     = data,
                             submit = submit(value = 'Add', name = 'process_data'))
        

class view(BaseUser):
    htmlplugin = adduserform
    
    def __init__(self, *args, **kwargs):
        super(view, self).__init__(*args, **kwargs)
        self._form = RegisterForm
        
    def title(self):
        site = SiteConfiguration.get_current()
        return 'Create a new %s account' % site.name
        
    def process_data(self):
        return self.process(self.add_user)
    
    def add_user(self, fdata, data):
        user = User.objects.create_user(data['username'],data['email_address'],data['password'])
        user.save()
        self.create_profile(user, data) 
        
    def create_provile(self, user, data):
        pass
