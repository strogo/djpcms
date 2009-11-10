
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

MARKUP_HANDLERS = {}
default_markup  = None


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


class ContentWrapper(object):
    '''
    Class responsible for wrapping djpcms plugins
    '''
    def __init__(self, name, handler, description = None):
        self.name = u'%s' % name
        self.description = u'%s' % (description or '',)
        self.handler = handler

    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return str(self.__unicode__())
    
    def __repr__(self):
        return self.__str__()
    
    def render(self, html):
        return mark_safe(forceunicode(self.handler.wrap(html)))
        
    def __eq__(self, other):
        if isinstance(other,ContentWrapper) and other.name == self.name:
            return True
        else:
            return False


class ContentWrapperHandler(object):
    
    def wrap(self, html):
        return html


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


#just add the default handler
add_content_wrapper('simple no tags',ContentWrapperHandler())

