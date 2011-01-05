from djpcms.views import appsite, appview
from djpcms.apps.included.user.views import *

permission = lambda self, request, obj: False if not request else request.user.is_authenticated()

class UserApplication(appsite.ModelApplication):
    name     = 'account'
    userpage = False
    form     = PasswordChangeForm
    
    home   = appview.ModelView()
    login  = LoginView(parent = 'home')
    logout = LogoutView(parent = 'home')
    change = appview.EditView(regex = 'change',
                              isplugin = True,
                              parent = 'home')
    
    def objectbits(self, obj):
        if self.userpage:
            return {'username': obj.username}
        else:
            return {}
    
    def get_object(self, request, *args, **kwargs):
        if self.userpage:
            try:
                id = int(kwargs.get('username',None))
                return self.model.objects.get(username = username)
            except:
                return None
        else:
            return request.user
        
    def has_edit_permission(self, request = None, obj=None):
        return permission(self,request,obj)
    