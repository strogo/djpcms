from django.utils.importlib import import_module
from django.conf import settings

from djpcms.views.staticsite import handler

    
class DjpcmsRequestHandler(object):
    '''
    Process a djpcms powered request.
    This middleware should be the last one on the list of MIDDLEWARE_CLASSES
    '''
    def process_request(self, request):
        pass
    
    

