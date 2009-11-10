
from djpcms.settings import DEFAULT_CODE_BASKET

__all__ = ['getobject', 'unique_code_name', 'unique_code_value']


def unique_code_name(obj, namebasket = None):
    '''
    Return a unique attribute for object obj
    '''
    if namebasket == None:
        namebasket = DEFAULT_CODE_BASKET
    
    opts = obj._meta
    for c in namebasket:
        code = _try_unique_code_name(opts,c)
        if code:
            return code
        
    return opts.pk.attname

def unique_code_value(obj, namebasket = None):
    attr = unique_code_name(obj,namebasket)
    return getattr(obj,attr)
    
    


def getobject(model, cval, namebasket = None):
    code = unique_code_name(model,namebasket)
    if code == 'id':
        cval = int(cval)
    kwargs = {str(code): cval}
    try:
        return model.objects.get(**kwargs)
    except Exception:
        return None        


def _try_unique_code_name(opts, name):
    '''
    Utility function which test whether model meta 'opts' has a
    unique field with name 'name'
     opts     model meta class
     name     field to test
    '''
    try:
        attr = opts.get_field(name)
        if not attr.unique:
            return None
        return name
    except:
        return None


def _try_attribute_code_name(m,name):
    try:
        attr = getattr(m,name)
        if callable(attr):
            attr = attr()
        return name
    except:
        return None
