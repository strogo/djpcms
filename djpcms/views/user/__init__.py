
from djpcms.views import appsite, appview
from login import *

class UserApplication(appsite.ModelApplication):
    name    = 'account'
    baseurl = '/accounts/'
    home    = appview()
    login   = LoginApp(isplugin = True, parent = 'home')
    logout  = LogoutApp(parent = 'home')