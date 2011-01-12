from djpcms import sites
from djpcms.utils import force_str
from djpcms.utils.collections import OrderedDict
from djpcms.template import loader, mark_safe, conditional_escape
from djpcms.forms import Media


def flatatt(attrs):
    """
    Convert a dictionary of attributes to a single string.
    The returned string will contain a leading space followed by key="value",
    XML-style pairs.  It is assumed that the keys do not need to be XML-escaped.
    If the passed dictionary is empty, then return an empty string.
    """
    return ''.join([' {0}="{1}"'.format(k, conditional_escape(v)) for k, v in attrs.items()])


class htmlbase(object):
    
    def get_template(self):
        template = getattr(self,'template',None)
        if template:
            return template
        else:
            raise NotImplementedError
    
    def __repr__(self):
        return self.render()
    __str__ = __repr__
    
    def get_content(self):
        return {'html': self,
                'css':  sites.settings.HTML_CLASSES}
    
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
        return '' if not attrs else flatatt(attrs)
        
    def render(self):
        return loader.render_to_string(self.get_template(),
                                       self.get_content())
        
        
class htmlattr(htmlbase):
    '''
    HTML utility with attributes a la jQuery
    '''
    def __init__(self, cn = None, **attrs):
        self._attrs = attrs
        self.addClass(cn)
    
    def attrs(self):
        return self._attrs
    
    def addClasses(self, cn):
        cns = cn.split(' ')
        for cn in cns:
            self.addClass(cn)
        return self
    
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
        return '<{0}{1}/>'.format(self.tag,self.flatatt())
    
    
class htmlwrap(htmltag):
    '''
    wrap a string within a tag
    '''
    def __init__(self, tag, inner, **attrs):
        self.inner = inner
        super(htmlwrap,self).__init__(tag, **attrs)
    
    def render(self):
        return mark_safe(u'\n'.join(['<%s%s>' % (self.tag,self.flatatt()),
                                     self.inner,
                                     '</%s>' % self.tag]))
    
    
class htmlcomp(htmltag):
    '''
    HTML component with inner components
    '''
    def __init__(self, tag, template = None, inner = None, **attrs):
        super(htmlcomp,self).__init__(tag, **attrs)
        self.template = template
        self.tag      = tag
        self.inner    = OrderedDict()
        if inner:
            self['inner'] = inner
        
    def __setitem__(self, key, value):
        if isinstance(value, htmlbase):
            self.inner[key] = value
        
    def items(self):
        for v in self.inner.values():
            yield v
    
    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = Media()
        items = self.items()
        for item in items:
            m = getattr(item,'media',None)
            if m:
                media = media + m
        return media
    media = property(_get_media)
    
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
        
    
class input(htmltiny):
    
    def __init__(self, name = 'submit', value = 'submit', type = 'submit', **attrs):
        super(input,self).__init__('input', name = name, value = value,
                                    type = type, **attrs)

