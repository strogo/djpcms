from djpcms.conf import settings
from djpcms.views import appsite, appview
from djpcms.views.apps.user.views import *

class UserApplication(appsite.ModelApplication):
    name     = 'account'
    userpage = False
    baseurl  = settings.USER_ACCOUNT_HOME_URL
    form     = PasswordChangeForm
    
    home    = appview.AppView()
    login   = LoginView(isplugin = True, parent = 'home')
    logout  = LogoutView(parent = 'home')
    change  = ChangeView(regex = 'change', isplugin = True, parent = 'home')
    
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