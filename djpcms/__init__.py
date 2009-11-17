import os
import sys
from djpcms.utils.deco import saferender

VERSION = (0, 4, 'beta')

def get_version():
    if VERSION[2] is not None:
        v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v

_Custom_response_methods = {}
siteapp_choices = [('','---------------'),('this','THIS')]

def functiongenerator():
    '''
    generator for iterating through rendering functions.
    Used in django.Forms
    '''
    global _Custom_response_methods
    for m in _Custom_response_methods.values():
        yield (m.name,m.description)


def register_view_method(method):
    '''
    Register a new rendering function
    '''
    global _Custom_response_methods
    name = method.name or method.__name__
    method.name = name
    description = method.description or name
    method.description = description
    if not _Custom_response_methods.has_key(name):
        _Custom_response_methods[name] = method()


def custom_response(name):
    global _Custom_response_methods
    return _Custom_response_methods.get(name,None)
        

def install():
    pp = os.path.join(os.path.dirname(__file__),'plugins')
    if pp not in sys.path:
        sys.path.insert(0, pp)


install()
__version__ = get_version()