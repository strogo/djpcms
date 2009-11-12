
from djpcms.utils.markups.cwrap import ContentWrapper, SimpleWrapHandler

def addmarkup(code, name, handler):
    global default_markup, MARKUP_HANDLERS
    if not default_markup:
        default_markup = code
    if not MARKUP_HANDLERS.has_key(code): 
        MARKUP_HANDLERS[code] = {'name': name,
                                 'handler': handler}

def markup_choices():
    global MARKUP_HANDLERS
    tup = []
    for k,v in MARKUP_HANDLERS.items():
        tup.append((k,v.get('name')))
    return tup


def add_content_wrapper(name, handler, description = None):
    global CONTENT_WRAP_HANDLERS
    cw = ContentWrapper(name,handler)
    if cw not in CONTENT_WRAP_HANDLERS:
        CONTENT_WRAP_HANDLERS.append(cw)


def content_warpper_tuple():
    '''
    Return a tuple of 2 elements tuples. Used in form choice field
    '''
    global CONTENT_WRAP_HANDLERS
    tup = []
    i   = 0
    for c in CONTENT_WRAP_HANDLERS:
        tup.append((0,c.name))
    return tuple(tup)


CONTENT_WRAP_HANDLERS = []
default_markup  = None
MARKUP_HANDLERS = {}


#just add the default wrapper
add_content_wrapper('simple no tags',SimpleWrapHandler())
