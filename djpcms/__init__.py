import os
import sys

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
    for k in _Custom_response_methods:
        yield (k,k)

def register_view_method(func, name = None):
    global _Custom_response_methods
    name = name or func.__name__
    if not _Custom_response_methods.has_key(name):
        _Custom_response_methods[name] = func

def custom_response(name):
    global _Custom_response_methods
    return _Custom_response_methods.get(name,None)
        

def install():
    pp = os.path.join(os.path.dirname(__file__),'plugins')
    if pp not in sys.path:
        sys.path.insert(0, pp)


install()
__version__ = get_version()