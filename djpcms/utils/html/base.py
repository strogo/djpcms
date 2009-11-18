
from django.template import loader, Context
from django.forms.util import flatatt
from django.utils.datastructures import SortedDict

from djpcms.settings import HTML_CLASSES

class htmlbase(object):
    ajax = HTML_CLASSES
    
    def get_template(self):
        raise NotImplementedError
    
    def get_content(self):
        return {'html': self,
                'css':  self.ajax}
    
    def getplugins(self, ftype):
        return None
    
    def items(self):
        return []
    
    def attrs(self):
        return None
    
    def addClass(self, cn):
        return self
    
    def hasClass(self, cn):
        return False
                
    def removeClass(self, cn):
        return self
    
    def flatatt(self):
        _attrs = self.attrs()
        if _attrs:
            attrs = {}
            for k,v in _attrs.items():
                if v:
                    attrs[k] = v
            if attrs:
                return mark_safe(u'%s' % flatatt(attrs))
        return u''
        
    def render(self):
        return loader.render_to_string(self.get_template(),
                                       self.get_content())
        
        
class htmlattr(htmlbase):
    '''
    HTML utility with attributes a la jQuery
    '''
    def __init__(self, id = None, cn = None, name = None):
        self._attrs = {}
        if id:
            self._attrs['id'] = id
        if name:
            self._attrs['name'] = name
        self.addclass(cn)
        
    def attr(self):
        return self._attrs
        
    def addClass(self, cn):
        if cn:
            attrs = self._attrs
            c    = attrs['class']
            if c:
                attrs['class'] = '%s %s' % (c,cn)
            else:
                attrs['class'] = cn
        return self
    
    def hasClass(self, cn):
        css = self._attrs['class'].split(' ')
        return cn in css
                
    def removeClass(self, cn):
        '''
        remove a class name from attributes
        '''
        css = self._attrs['class'].split(' ')
        for i in range(0,len(css)):
            if css[i] == cn:
                css.pop(i)
                break
        self._attrs['class'] = ' '.join(css)
        return self
    
    
def htmlcomp(htmlattr):
    '''
    HTML component with inner components
    '''
    def __init__(self, **attrs):
        super(htmlcomp,self).__init__(**attrs)
        self.inner = SortedDict()
        
    def __setitem__(self, key, value):
        if isinstance(value, htmlbase):
            self.inner[key] = value
        
    def items(self):
        for v in self.inner.values():
            yield v
            
    def getplugins(self, ftype):
        '''
        Return a list of plugings of type ftype
        '''
        fs = []
        for c in self.inner.values():
            if isinstance(c,ftype):
                fs.append(c)
            elif isinstance(c,htmlcomp):
                fs.extend(c.getplugins(ftype))
        return fs
        