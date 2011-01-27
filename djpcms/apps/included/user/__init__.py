from djpcms.views import appsite, appview
from djpcms.forms import HtmlForm
from djpcms.apps.included.user.views import *

permission = lambda self, request, obj: False if not request else request.user.is_authenticated()


class UserApplication(appsite.ModelApplication):
    '''This is a special Application since it deals with users and therefore is everywhere.
No assamtion has been taken of which model it is used for storing user data as long as
there is a common interface for common operations.'''
    name     = 'account'
    userpage = False
    form     = PasswordChangeForm
    
    home   = appview.ModelView()
    login  = LoginView(parent = 'home')
    logout = LogoutView(parent = 'home')
    change = appview.EditView(regex = 'change',
                              isplugin = True,
                              parent = 'home',
                              form = HtmlForm(PasswordChangeForm))
    add = appview.AddView(regex = 'create',
                          isplugin = True,
                          parent = 'home',
                          form = HtmlForm(RegisterForm))
    
    def registration_done(self):
        self.application_site.User = self.opts
    
    def objectbits(self, obj):
        if self.userpage:
            return {'username': obj.username}
        else:
            return {}
    
    def get_object(self, request, *args, **kwargs):
        if self.userpage:
            try:
                username = kwargs.get('username',None)
                return self.model.objects.get(username = username)
            except:
                return None
        else:
            return request.user
        
    def has_edit_permission(self, request = None, obj=None):
        return permission(self,request,obj)
    