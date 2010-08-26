
from djpcms.views import appsite, appview
from login import *

class UserApplication(appsite.ModelApplication):
    name    = 'account'
    baseurl = '/accounts/'
    home    = appview.AppView()
    login   = LoginView(isplugin = True, parent = 'home')
    logout  = LogoutView(parent = 'home')