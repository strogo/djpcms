from djpcms.utils.collections import OrderedDict

from .globals import *


__all__ = ['Form','Factory']
    

class Form(object):
    '''base class for forms. This class is created by instances
of a :class:`Factory`'''
    def __init__(self,factory,data,files,initial,prefix):
        self.is_bound = data is not None or files is not None
        self.factory = factory
        self.rawdata = data
        self._files = files
        self.initial = initial
        self.prefix = prefix or ''
    
    @property
    def data(self):
        self._validate()
        return self._data

    @property
    def cleaned_data(self):
        self._validate()
        return self._cleaned_data
        
    @property
    def errors(self):
        self._validate()
        return self._errors
    
    @property
    def fields(self):
        self._validate()
        return self._fields
    
    def _validate(self):
        if hasattr(self,'_data'):
            return
        self._data = data = {}
        cleaned = {}
        self._errors = errors = {}
        tempdata = self.rawdata.copy()
        self._fields = fields = OrderedDict()
        
        if self.is_bound:
            prefix = self.prefix
            np = len(prefix) 
            for field in self.factory.fields:
                name = field.name
                key = name
                if prefix:
                    key = prefix+name
                try:
                    value = field.clean(tempdata.pop(key,nodata))
                    cleaned[name] = value
                except ValidationError:
                    errors.append(field)
                data[name] = value
            if not errors:
                self._cleaned_data = cleaned
        else:
            initial = self.initial
            for field in self.factory.fields:
                name = field.name
                if name in initial:
                    bfield = field(self,initial[name])
                else:
                    bfield = field(self)
                fields[name] = bfield
            
    def is_valid(self):
        return self.is_bound and not self.errors
    
    def render(self):
        layout = self.factory.layout
        if not layout:
            layout = DefaultLayout()
            self.factory.layout = layout
        return layout.render(self)
            

class Factory(object):
    '''Form factory Creator'''
    prefix_input = '_prefixed'
    
    def __init__(self, *fields, **kwargs):
        self.fields = fields
        self.setup(**kwargs)
        
    def setup(self, form_class = None, layout = None, model = None, **kwargs):
        self.form_class = form_class or Form
        self.model = model
        self.layout = layout
        
    def get_prefix(self, prefix, data):
        if data and self.prefix_input in data:
            return data[self.prefix_input]
        elif prefix:
            if hasattr(prefix,'__call__'):
                prefix = prefix()
            return prefix
        else:
            return ''
        
    def __call__(self, data = None, files = None, 
                 initial = None, instance = None,
                 prefix = None):
        prefix = self.get_prefix(prefix,data)
        return self.form_class(self,data,files,initial,prefix)

