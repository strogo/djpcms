from django.utils.importlib import import_module
from django.conf import settings

from djpcms.views.staticsite import handler

    
class StaticPagesMiddleware(object):
    '''
    Check For static Pages.
    If a static page is found return response object, otherwise return None
    '''
    pass

