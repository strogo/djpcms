
from djpcms.views import appsite
from login import *

class UserApplication(appsite.ModelApplication):
    name    = 'account'
    baseurl = '/accounts/'
    login   = LoginApp()
    logout  = LogoutApp()