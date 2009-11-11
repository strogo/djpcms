from login import *



from djpcms.plugins.application.appsite.options import ModelApplication


class UserApplication(ModelApplication):
    name    = 'account'
    baseurl = '/accounts/'
    login   = LoginApp()
    logout  = LogoutApp()