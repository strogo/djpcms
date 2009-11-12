
from djpcms.plugins.application import appsite
from djpcms.views.appview import AppView


class CloudApp(AppView):
    
    def __init__(self, *args, **kwargs):
        super(CloudApp,self).__init__(*args, **kwargs)
    
    def render(self, request, prefix, wrapper, *args):
        '''
        Render a tag cloud
        '''
        args     = self.args or args
        

class TagApplication(appsite.ModelApplicationBase):
    name    = 'tags'
    baseurl = '/tags/'
    cloud   = CloudApp()