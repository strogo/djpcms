from djpcms.conf import settings
from djpcms.views import appsite, appview
from login import *

class UserApplication(appsite.ModelApplication):
    name    = 'account'
    baseurl = settings.USER_ACCOUNT_HOME_URL
    home    = appview.AppView()
    login   = LoginView(isplugin = True, parent = 'home')
    logout  = LogoutView(parent = 'home')