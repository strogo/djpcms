
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
    
    
def slugify(value, rtx = '-'):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return mark_safe(re.sub('[-\s]+', rtx, value))



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
    
