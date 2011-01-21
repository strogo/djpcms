from djpcms.utils import slugify, merge_dict
from djpcms.utils.py2py3 import iteritems
from djpcms.template import loader, mark_safe, conditional_escape

from .media import BaseMedia

__all__ = ['flatatt',
           'HtmlWidget']

def flatatt(attrs):
    def itera():
        for k,v in attrs.items():
            if v:
                if k == 'class':
                    v = ' '.join(v)
                yield ' {0}="{1}"'.format(k, conditional_escape(v))
    
    return ''.join(itera())


class HtmlWidget(BaseMedia):
    default_style = None
    attributes = {'id':None}
    
    def __init__(self, cn = None, template = None, **kwargs):
        attrs = {}
        self.template = template
        for attr,value in iteritems(self.attributes):
            if attr in kwargs:
                value = kwargs[value]
            attrs[attr] = value
        self.default_style = kwargs.get('default_style',self.default_style)
        self.__attrs = attrs
        self.__classes = set()
        self.__attrs['class'] = self.__classes
        self.addClass(cn)
        
    def flatatt(self):
        return flatatt(self.__attrs)
        
    @property
    def attrs(self):
        return self.__attrs
    
    def addClasses(self, cn, splitter = ' '):
        cns = cn.split(splitter)
        for cn in cns:
            self.addClass(cn)
        return self
    
    def addClass(self, cn):
        if cn:
            cn = slugify(cn)
        if cn:
            self.__classes.add(cn)
        return self
    
    def hasClass(self, cn):
        return cn in self.__classes
                
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

    
class FormWidget(HtmlWidget):
    default_style = None
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'method':'post',
                                                    'enctype':'multipart/form-data',
                                                    'action': '.'
                                                    })
    def __init__(self, *fields, **kwargs):
        super(FormWidget,self).__init__(**kwargs)
        self._allfields = []
        self.inlines    = []
        self.add(*fields)
        
    def add(self,*fields):
        pass
    
    