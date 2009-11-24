
from django.template import loader, Context
from django.forms.util import flatatt
from django.utils.datastructures import SortedDict
from django.utils.safestring import mark_safe

from djpcms.settings import HTML_CLASSES
from djpcms.utils import UnicodeObject


class htmlbase(UnicodeObject):
    ajax = HTML_CLASSES
    
    def get_template(self):
        template = getattr(self,'template',None)
        if template:
            return template
        else:
            raise NotImplementedError
    
    def __unicode__(self):
        return self.render()
    
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
        attrs = self.attrs()
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
    def __init__(self, id = None, cn = None, name = None, value = None):
        self._attrs = {}
        if id:
            self._attrs['id'] = id
        if name:
            self._attrs['name'] = name
        if value:
            self._attrs['value'] = value
        self.addClass(cn)
    
    def attrs(self):
        return self._attrs
        
    def addClass(self, cn):
        if cn:
            cn = str(cn).replace(' ','')
        if cn:
            attrs = self._attrs
            c    = attrs.get('class',None)
            if c:
                cs = c.split(' ')
                if cn not in cs:
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
    

class htmltag(htmlattr):
    
    def __init__(self, tag, **attrs):
        self.tag = tag
        super(htmltag,self).__init__(**attrs)


class htmltiny(htmltag):
    
    def __init__(self, tag, **attrs):
        super(htmltiny,self).__init__(tag, **attrs)
    
    def render(self):
        return mark_safe(u'<%s%s/>' % (self.tag,self.flatatt()))
    
class htmlsmall(htmltag):
    
    def __init__(self, tag, inner, **attrs):
        self.inner = inner
        super(htmlsmall,self).__init__(tag, **attrs)
    
    def render(self):
        return mark_safe(u'<%s%s>%s</%s>' % (self.tag,self.flatatt(),self.inner,self.tag))
    
    
class htmlcomp(htmltag):
    '''
    HTML component with inner components
    '''
    def __init__(self, tag, template = None, inner = None, **attrs):
        super(htmlcomp,self).__init__(tag, **attrs)
        self.template = template
        self.tag      = tag
        self.inner    = SortedDict()
        if inner:
            self['inner'] = inner
        
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
    
    def get_template(self):
        if self.template:
            return self.template
        top = 'components/%s.html' % self.tag
        return [top,
                'djpcms/%s' % top,
                'components/htmlcomp.html',
                'djpcms/components/htmlcomp.html']