
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.template import Context, Template


__all__ = ['ContentWrapperHandler',
           'add_content_wrapper',
           'content_wrapper_tuple',
           'CONTENT_WRAP_HANDLERS']



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
    
    def wrap(self, cblock, cl):
        return mark_safe(self.handler.wrap(cblock, cl))
        
    def __eq__(self, other):
        if isinstance(other,ContentWrapper) and other.name == self.name:
            return True
        else:
            return False


class ContentWrapperHandler(object):
    '''
    Content wrapper
    '''
    form_layout = None
    
    def inner(self, cblock, cl):
        '''
        Render the inner block
        '''
        return cblock.render(cl)
    
    def wrap(self, cblock, cl):
        '''
        Wrap content for block cblock
        @param param: cblock instance or BlockContent or AppBlockContent
        @param request: HttpRequest instance
        @param view: instance of djpcmsview  
        '''
        return self.inner(cblock, cl)


def add_content_wrapper(name, handler, description = None):
    global CONTENT_WRAP_HANDLERS
    cw = ContentWrapper(name,handler)
    if cw not in CONTENT_WRAP_HANDLERS:
        CONTENT_WRAP_HANDLERS.append(cw)
        

class content_wrapper_tuple(object):
    '''
    Return a tuple of 2 elements tuples. Used in form choice field
    '''            
    def __iter__(self):
        global CONTENT_WRAP_HANDLERS
        i   = 0
        for c in CONTENT_WRAP_HANDLERS:
            yield (i,c.name)
            i += 1


CONTENT_WRAP_HANDLERS = []


#just add the default handler
add_content_wrapper('simple no tags',ContentWrapperHandler())





