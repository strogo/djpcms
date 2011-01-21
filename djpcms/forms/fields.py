from copy import deepcopy
from djpcms import sites

from .globals import *

__all__ = ['Field',
           'CharField']


def standard_validation_error(field,value):
    if value == novalue:
        return 'Field {0} is required'.format(field.name)
    else:
        return str(value)
    

class Field(object):
    default = None
    
    def __init__(self,
                 name,
                 required = True,
                 default = None,
                 validation_error = None,
                 help_text = None,
                 label = None,
                 **kwargs):
        self.name = name
        self.default = default or self.default
        self.required = required
        self.validation_error = validation_error or standard_validation_error
        self.help_text = help_text
        self.label = label or self.name
        self._handle_params(**kwargs)
        
    def _handle_params(self, **kwargs):
        self._raise_error(kwargs)
        
    def _raise_error(self, kwargs):
        keys = list(kwargs)
        if keys:
            raise ValueError('Parameter {0} not recognized'.format(keys[0]))
        
    def __call__(self, form):
        f = deepcopy(self)
        f.form = form
        if f.name in form.initial:
            f.value = form.initial[self.name]
        else:
            self.value = novalue
        return f
    
    def validate(self, value):
        if value == novalue or not value:
            if not required:
                default = self.default
                if hasattr(default,'__call__'):
                    default = default()
                return default
            else:
                raise ValidationError(self.validation_error(self,novalue))
        return self._validate(value)
    
    def _validate(self, value):
        return value
        
        
class CharField(Field):
    
    def _handle_params(self, max_length = None, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'.format(self.__class__.__name__))
        self.max_length = int(max_length)
        if self.max_length <= 0:
            raise ValueError('max_length must be positive')
        self._raise_error(kwargs)
        
    def _validate(self, value):
        try:
            return str(value)
        except:
            raise ValidationError



to_implement = ['IntegerField',
           'FloatField',
           'DateField',
           'DateTimeField',
           'BooleanField',
           'CharField',
           'FileField',
           'RegexField',
           'EmailField',
           'ChoiceField',
           'LazyAjaxChoice',
           'ModelCharField',
           'SlugField',
           'BoundField']

