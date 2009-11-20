
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.template import Context, Template

from djpcms.utils import UnicodeObject


__all__ = ['ContentWrapper',
           'add_content_wrapper',
           'content_wrapper_tuple',
           'CONTENT_WRAP_HANDLERS',
           'default_content_wrapper']



class ContentWrapper(UnicodeObject):
    '''
    Class responsible for wrapping djpcms plugins
    '''
    form_layout = None
    
    def __new__(cls, name = None, description = None):
        obj = super(ContentWrapper,cls).__new__(cls)
        name        = name or obj.__class__.__name__
        description = description or name
        obj.name = u'%s' % name
        obj.description = u'%s' % description
        return obj

    def __unicode__(self):
        return self.description
    
    def wrap(self, djp, cblock, html):
        '''
        Render the inner block. This function is the one to implement
        '''
        return html
    
    def __call__(self, djp, cblock, html):
        '''
        Wrap content for block cblock
        @param param: djp instance of djpcms.views.baseview.DjpRequestWrap 
        @param param: cblock instance or BlockContent
        @return: safe unicode HTML
        '''
        return mark_safe(self.wrap(djp, cblock, html))


def add_content_wrapper(handler, name = None, description = None):
    global CONTENT_WRAP_HANDLERS
    if not isinstance(handler,ContentWrapper):
        handler = handler(name,description)
    if not CONTENT_WRAP_HANDLERS.has_key(handler.name):
        CONTENT_WRAP_HANDLERS[handler.name] = handler
        

class content_wrapper_tuple(object):
    '''
    Return a tuple of 2 elements tuples. Used in form choice field
    '''            
    def __iter__(self):
        global CONTENT_WRAP_HANDLERS
        for c in CONTENT_WRAP_HANDLERS.values():
            yield (c.name,c.description)


CONTENT_WRAP_HANDLERS = {}


#just add the default handler
default_content_wrapper = ContentWrapper('simple','simple no tags')
add_content_wrapper(default_content_wrapper)





