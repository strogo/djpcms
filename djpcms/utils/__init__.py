import re
import json
import unicodedata
from uuid import uuid4

from .strings import *
from .jsontools import *
from .numbers import *


def gen_unique_id():
    return str(uuid4())


def merge_dict(d1,d2):
    d = d1.copy()
    d.update(d2)
    return d


def construct_search(field_name):
    # use different lookup methods depending on the notation
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name


def isexact(bit):
    if not bit:
        return bit
    N = len(bit)
    Nn = N - 1
    bc = '%s%s' % (bit[0],bit[Nn])
    if bc == '""' or bc == "''":
        return bit[1:Nn]
    else:
        return bit


def function_module(dotpath, default = None):
    '''
    Load a function from a module.
    If the module or the function is not available, return the default argument
    '''
    if dotpath:
        bits = str(dotpath).split('.')
        try:
            module = __import__('.'.join(bits[:-1]),globals(),locals(),[''])
            return getattr(module,bits[-1],default)
        except Exception as e:
            return default
    else:
        return default
    
    
def lazyattr(f):
    
    def wrapper(obj, *args, **kwargs):
        name = '_lazy_%s' % f.__name__
        try:
            return getattr(obj,name)
        except:
            v = f(obj, *args, **kwargs)
            setattr(obj,name,v)
            return v
    return wrapper


class lazyjoin(object):
    
    def __init__(self, sep):
        self.sep = sep
        
    def __call__(self, f):
        
        def _(obj, *args, **kwargs):
            return self.sep.join(f(*args,**kwargs))
        
        return _
        

def setlazyattr(obj,name,value):
    name = '_lazy_%s' % name
    setattr(obj,name,value)
    
    
@lazyjoin('/')
def safepath(path, rtx = '-'):
    for p in path.split('/'):
        if p:
            yield slugify(p, rtx = rtx)


def urlbits(url):
    if url.endswith('/'):
        url = url[:-1]
    if url.startswith('/'):
        url = url[1:]
    return url.split('/')


def urlfrombits(bits):
    if bits:
        return '/%s/' % '/'.join(bits)
    else:
        return '/'
    

class UnicodeObject(object):
    
    def __repr__(self):
        try:
            u = stringtype(self)
        except:
            u = '[Bad Unicode data]'
        return smart_str('<{0}: {1}>'.format(self.__class__.__name__, u))

    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_str(self).encode('utf-8')
        return '{0} object'.format(self.__class__.__name__)

    
def slugify(value, rtx = '-'):
    '''Normalizes string, removes non-alpha characters,
and converts spaces to hyphens *rtx* character'''
    value = unicodedata.normalize('NFKD', force_str(value)).encode('ascii', 'ignore')
    value = force_str(re.sub('[^\w\s-]', '', value).strip())
    return re.sub('[-\s]+', rtx, value)


def logerror(logger, request, exc_info):
    logger.error('Internal Server Error: %s' % request.path,
                 exc_info=exc_info,
                 extra={
                        'status_code': 500,
                        'request':request
                        }
                 )
