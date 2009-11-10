from djpcms.html import quickform
from djpcms.ajax import jredirect

from forms import PasswordForm
from tools import BaseUser, nice_name


class view(BaseUser):
    '''
    A change password view.
    '''        
    def title(self):
        fn = nice_name(self.object)
        return "%s's account Change password" % fn
    
    def get_form(self, request, data = None):
        return quickform(form = PasswordForm,
                         submitname  = 'change_password',
                         submitvalue = 'Change',
                         view = self,
                         data = data,
                         request = request)
    
    def change_password(self, request, data):
        f = self.get_form(request, data)
        if f.is_valid():
            f.save()
            return jredirect(self.factory.url)
        else:
            return f.jerrors

