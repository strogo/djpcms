'''Lightweight form library

Several parts are originally from django
'''
from djpcms.utils.collections import OrderedDict

from .globals import *
from .fields import Field
from .html import media_property


__all__ = ['Form',
           'FormFactory']


def get_declared_fields(bases, attrs, with_base_fields=True):
    """Adapted form djago
    """
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]
    fields.sort(key=lambda x: x[1].creation_counter)

    # If this class is subclassing another Form, add that Form's fields.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if with_base_fields:
        for base in bases[::-1]:
            if hasattr(base, 'base_fields'):
                fields = base.base_fields.items() + fields
    else:
        for base in bases[::-1]:
            if hasattr(base, 'declared_fields'):
                fields = base.declared_fields.items() + fields

    return OrderedDict(fields)


class DeclarativeFieldsMetaclass(type):
    """
    Metaclass that converts Field attributes to a dictionary called
    'base_fields', taking into account parent class 'base_fields' as well.
    """
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        new_class = super(DeclarativeFieldsMetaclass,cls).__new__(cls, name, bases, attrs)
        if 'media' not in attrs:
            new_class.media = media_property(new_class)
        return new_class
    

BaseForm = DeclarativeFieldsMetaclass('BaseForm',(object,),{})    


class Form(BaseForm):
    '''base class for forms. This class is created by instances
of a :class:`Factory`'''
    def __init__(self, data = None, files = None,
                 initial = None, prefix = None,
                 factory = None):
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
            

class FormFactory(object):
    prefix_input = '_prefixed'
    
    def __init__(self, form_class, layout = None, model = None):
        self.form_class = form_class
        self.layout = layout
        self.model = model
        
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

