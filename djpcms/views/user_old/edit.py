from djpcms.ajax import jredirect
from djpcms.html import form, formlet, submit, div

from tools import BaseUser, nice_name
from forms import UserChangeForm

class editform(form):
    '''
    '''
    def __init__(self, **attrs):
        super(editform,self).__init__(**attrs)
        
    def _createform(self, data = None, instance = None, **kwargs):
        self.addclass('aligned')
        co = self.make_container(div, cn = self.classes.search_entry)
        if instance:
            co['userform']  = formlet(form     = self.view._form,
                                      data     = data,
                                      instance = instance)
            self.addpreferences(co, data, instance)
            co['submit'] = formlet(submit = submit(value = 'Change', name = 'process_data'))
            
    def addpreferences(self, co, data, instance):
        pass
            
        
class view(BaseUser):
        
    def title(self):
        fn = nice_name(self.object)
        return "Edit %s's account" % fn
    
    def get_form(self, request, data = None):
        return self.editform(view = self, data = data, request = request)
    
    def process_data(self, request):
        return self.process(self.change_user)
    
    def change_user(self, fdata, data):
        fdata.save()
        return jredirect(self.factory.url)