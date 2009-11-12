
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

class ContentWrapper(object):
    '''
    Class responsible for wrapping djpcms contents
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
        
        
class SimpleWrapHandler(object):
    '''
    Do nothing
    '''
    def wrap(self, html):
        return html