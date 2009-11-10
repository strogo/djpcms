from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.template import loader


__all__ = ['ajaxbase','htmlPlugin','div','ul','link','button',
           'TemplatePlugin','compactTag','spanlink','get_ajax']

def get_ajax():
    from djpcms.settings import HTML_CLASSES
    return HTML_CLASSES


class htmlPluginNotFound(Exception):
    pass

class htmlBadKey(Exception):
    pass


def create_new_plugin(cls, *args, **attrs):
    # obsolete call
    #obj     = super(htmlPlugin, cls).__new__(cls, *args, **attrs)
    obj     = super(htmlPlugin, cls).__new__(cls)
    cn     = attrs.pop('cn','')
    id     = attrs.pop('id','')
    url    = attrs.pop('url',None)
    inner  = attrs.pop('inner',None)
    object = attrs.pop('object',None)
    if object:
        model = object.__class__
    else:
        model  = attrs.pop('model',None)
    view    = attrs.pop('view',None)
    request = attrs.pop('request',None)
    tag     = attrs.pop('tag',None)
    tmpl    = attrs.pop('template',None)
    obj.children     = []
    obj.parent       = None
    obj.url          = url
    #if view:
    #    if not url:
    #        obj.url = view.url
    #    if not model:
    #        model  = view.model
    #        object = view.object
    obj._viewholder    = view
    obj.tag            = obj.tag or tag
    obj.template       = tmpl
    obj.request        = request
    obj.model          = model
    obj.object         = object
    obj._preprocessed  = False
    obj.attrs          = {'class': cn, 'id': id}
    obj.append(inner)
    return obj
    
    
class ajaxbase(object):
    
    def __get_ajax(self):
        return get_ajax()
    ajax = property(fget = __get_ajax)
        


class htmlPlugin(ajaxbase):
    '''
    Interface class for html plugins
    '''
    #__metaclass__ = htmlMeta
    tag = None
    
    def __new__(cls, *args, **attrs):
        return create_new_plugin(cls, *args, **attrs)
    
    def __iter__(self):
        return self.children.__iter__()
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, self.info())
    
    def __get_ajax(self):
        from djpcms.settings import HTML_CLASSES
        return HTML_CLASSES
    ajax = property(fget = __get_ajax)
    
    def render_as_widget(self):
        '''
        Wrap the html so that it can be displayed as a stand-alone
        element on a html grid
        '''
        wc = self.ajax.GRID_WIDGET_CLASS
        if not self.hasclass(wc):
            el = htmlPlugin(tag = 'div', cn = wc)
            self.wrap_internal_widget(el).append(self)
        else:
            # Do nothing
            el = self
        return loader.render_to_string('djpcms/layouts/bits/grid-widget.html',
                                       {'html': el.render(),
                                        'wrap': True})
    
    def wrap_internal_widget(self, el):
        il1 = htmlPlugin(tag = 'div',
                         cn = self.ajax.grid_widget_inner).appendTo(el)
        return htmlPlugin(tag = 'div',
                          cn = self.ajax.wwrap).appendTo(il1)
        
        
    
    
    def __get_view(self):
        return self._viewholder
    view = property(fget = __get_view)
    
    def __str__(self):
        return '%s' % self.__unicode__()
    
    def __unicode__(self):
        return self.render()
    
    def __len__(self):
        return len(self.children)
    
    def info(self):
        return self.render()
    
    def defauts(self):
        return {}
    
    def getplugins(self, ftype):
        '''
        Return a list of plugings of type ftype
        '''
        fs = []
        for c in self:
            if isinstance(c,ftype):
                fs.append(c)
            elif isinstance(c,htmlPlugin):
                fs.extend(c.getplugins(ftype))
        return fs
    
    def rendertop(self):
        tag = self.tag
        if not tag:
            return ''
        else:
            attrs = self.flatatt()
            return mark_safe(u'<%s%s>' % (tag,attrs))
        
    def prerender(self):
        '''
        Override this function to allow for preprocessing of
        children before rendering
        '''
        pass
    
    def opentag(self):
        tag = self.tag
        if not tag:
            return ''
        attrs = self.flatatt()
        return mark_safe(u'<%s%s>' % (tag,attrs))
    
    def closetag(self):
        tag = self.tag
        if not tag:
            return ''
        return mark_safe(u'</%s>' % tag)
    
    def render(self):
        if not self._preprocessed:
            self._preprocessed = True
            self.prerender()
        tag = self.tag
        if not tag:
            return self.innerrender()
        attrs = self.flatatt()
        a1    = u'<%s%s>' % (tag,attrs)
        a2    = self.innerrender()
        a3    = u'</%s>' % tag
        if tag in ('div','ul'):
            if a2:
                html = u'\n'.join([a1,a2,a3])
            else:
                html = u'\n'.join([a1,a3])
        else:
            html = u'%s%s%s' % (a1,a2,a3)
        return mark_safe(html)
    
    def flatatt(self):
        attrs = {}
        for k,v in self.attrs.items():
            if v:
                attrs[k] = v
        if attrs:
            a = flatatt(attrs)
        else:
            a = ''
        return mark_safe(u'%s' % a)
        
    def innerrender(self):
        if not len(self):
            return ''
        
        html = []
        for c in self:
            if hasattr(c,'render'):
                html.append(c.render())
            else:
                try:
                    html.append(mark_safe(force_unicode(c)))
                except Exception:
                    pass
        return mark_safe(u'\n'.join(html))
    
    def addclass(self, cn):
        if cn:
            attrs = self.attrs
            c    = attrs['class']
            if c:
                attrs['class'] = '%s %s' % (c,cn)
            else:
                attrs['class'] = cn
        return self
    
    def hasclass(self, cn):
        css = self.attrs['class'].split(' ')
        return cn in css
                
    def removeclass(self, cn):
        '''
        remove a class name from attributes
        '''
        css = self.attrs['class'].split(' ')
        for i in range(0,len(css)):
            if css[i] == cn:
                css.pop(i)
                break
        self.attrs['class'] = ' '.join(css)
        return self
                
    def __setitem__(self, key, html):
        if not key:
            raise htmlBadKey('Key not valid')
        if not hasattr(self,key):
            if html != None:
                object.__setattr__(self,key,html)
                self.append(html)
        else:
            raise htmlBadKey('Key already available')
        
    def append(self, html):
        '''
        Append html to self
        '''
        if html == None:
            return self
        self.children.append(html)
        return self
    
    def reverse(self):
        self.children.reverse()
    
    def appendTo(self, html):
        '''
        Append self to html
        '''
        if html == None:
            return self
        html.append(self)
        return self
    
    def attr(self, *args, **kwargs):
        '''
        set or get attributes (a-la jQuery)
        '''
        if kwargs:
            # we set attributes and return self 'a la jQuery'
            for k,v in kwargs.items():
                if v:
                    self.attrs[k] = v
            return self
        elif len(args) == 1:
            return self.attrs.get(args[0],None)
        else:
            return self
        
    def removeAttr(self, name):
        self.attrs.pop(name,None)
        return self
        
    def css(self, *args, **kwargs):
        if kwargs:
            att = ''
            for k,v in kwargs.items():
                att = '%s%s:%s;' % (att,k,v)
            self.attrs.update({'style':att})
        elif len(args) == 1:
            return self.attrs.get(args[0],None)
        return self
            
    def last(self):
        '''
        Return the last children
        '''
        if not self:
            return None
        return self.children[len(self)-1]
    
    def _render_template(self):
        '''
        Function which can be used to render from a template
        self can be accessed using {{ html }}
        '''
        return loader.render_to_string(self.template,
                                       {'html': self,
                                        'HTML_CLASSES': self.ajax})
        
            
            
            
    
    
class div(htmlPlugin):
    tag = 'div'


class ul(htmlPlugin):
    tag = 'ul'
    
    
class link(htmlPlugin):
    tag = 'a'
    
    def __init__(self, target = None, **attrs):
        self.attrs['href'] = self.url
        if target:
            self.attrs['target'] = target
    
    def render(self):
        tag = self.tag
        attrs = self.flatatt()
        inner = self.innerrender()
        return mark_safe(u'<%s%s>%s</%s>' % (tag,attrs,inner,tag))
    
   
class button(link):
    tag = 'button'
    
    def __init__(self, **attrs):
        self.attrs['type'] = attrs.pop('type','button')
        
    
class compactTag(htmlPlugin):
    
    def render(self):
        tag = self.tag
        attrs = self.flatatt()
        return mark_safe(u'<%s%s/>' % (tag,attrs))
    
    
class TemplatePlugin(htmlPlugin):
    '''
    Plugin which render itself from a django template file
    '''
    def render(self):
        return self._render_template()


def spanlink(inner = '', **attrs):
    c = htmlPlugin(tag = 'span')
    inner = htmlPlugin(inner = c).append(inner)
    return link(inner = inner, **attrs)
    
