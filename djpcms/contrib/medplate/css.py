from copy import copy

from djpcms import template

class NoValue:
    pass


class CssContext(object):
    
    def __init__(self, name, tag = None, template = None,
                 description = '', elems= None,
                 data = None, ineritable_tag = True,
                 defaults = None):
        self.name = name
        self._tag = tag
        self._ineritable_tag = ineritable_tag
        self.template = template or 'medplate/elem.css_t'
        self.parent = None
        self.description = description or self._tag
        self.data = data or {}
        self.defaults = defaults or {}
        self.elems = []
        elems = elems or []
        for elem in elems:
            self.add(elem)
        
    def __str__(self):
        return self.render()

    def __repr__(self):
        return self.__str__()
    
    def tag(self):
        tag = ''
        if self.parent:
            tag = self.parent.ineritable_tag()
            if tag:
                tag += ' '
        return tag + self._tag
    
    def ineritable_tag(self):
        if self._ineritable_tag:
            return self.tag()
        else:
            return ''
    
    def render(self, template_engine = None):
        loader = template.handle(template_engine)
        return loader.render(self.template,self)
    
    def update(self, data):
        self.data.update(data)
        
    def copy(self):
        return copy(self)
    
    def add(self, value):
        if isinstance(value,CssContext):
            self.elems.append(value)
            value.parent = self
            self.data[value.name] = value
            
    def __iter__(self):
        return iter(self.data)
    
    def get(self, key, default = None):
        try:
            return getattr(self,key)
        except AttributeError:
            return default
        
    def __getattr__(self, key):
        v = self.data.get(key, NoValue)
        if v is NoValue:
            if self.parent:
                try:
                    v = getattr(self.parent,key)
                except AttributeError:
                    pass
                
            if v is NoValue:
                v = self.defaults.get(key, NoValue)
                if v is NoValue:
                    raise AttributeError('No attribute {0} avaialble'.format(key))
        
        return v
        
    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False
    
    def __getitem__(self, key):
        try:
            item = getattr(self,key)
            if hasattr(item,'__call__'):
                item = item()
            return item
        except AttributeError:
            raise KeyError
        
    def __copy__(self):
        obj = self.__class__(self.name,
                             self._tag,
                             self.template,
                             self.description,
                             data=self.data,
                             ineritable_tag = self._ineritable_tag,
                             defaults = self.defaults)
        for elem in self.elems:
            obj.add(copy(elem))
        return obj


