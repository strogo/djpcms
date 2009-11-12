from django.utils.encoding import smart_str, force_unicode, smart_unicode

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
