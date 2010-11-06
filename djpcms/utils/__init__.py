from django.utils.encoding import smart_str, force_unicode, smart_unicode
from django.utils.safestring import mark_safe
from anyjson import json


json_dump_safe = lambda data: mark_safe(force_unicode(json.dumps(data)))


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


class NoAjaxKeyError(Exception):
    
    def __init__(self, key):
        super(NoAjaxKeyError,self).__init__('Ajax key "%s" was not found' % key)


    

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
        except Exception, e:
            return default
    else:
        return default
    

def safepath(path, rtx = '-'):
    rpath = path.split('/')
    bits = []
    for p in rpath:
        if p:
            bits.append(slugify(p, rtx = rtx))
    return '/'.join(bits)
    
    
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

def setlazyattr(obj,name,value):
    name = '_lazy_%s' % name
    setattr(obj,name,value)
    
    
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
            u = unicode(self)
        except (UnicodeEncodeError, UnicodeDecodeError):
            u = '[Bad Unicode data]'
        return smart_str(u'<%s: %s>' % (self.__class__.__name__, u))

    def __str__(self):
        if hasattr(self, '__unicode__'):
            return force_unicode(self).encode('utf-8')
        return '%s object' % self.__class__.__name__

    
class requestwrap(UnicodeObject):
    
    def __init__(self, obj, request):
        self.request = request
        self.obj = obj
        
    def __unicode__(self):
        return unicode(self.obj)
        
    def __getattr__(self, name):
        attr = getattr(self.obj,name,None)
        if attr and callable(attr):
            # First we try using request as argument
            try:
                return attr(self.request)
            except:
                return attr()
        else:
            return attr


def slugify(value, rtx = '-'):
    import re
    import unicodedata
    '''Normalizes string, removes non-alpha characters,
and converts spaces to hyphens *rtx* character'''
    value = unicodedata.normalize('NFKD', unicode(value)).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return mark_safe(re.sub('[-\s]+', rtx, value))
