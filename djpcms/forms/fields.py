from copy import deepcopy
from djpcms import sites

from .globals import *

__all__ = ['Field',
           'CharField',
           'DateField',
           'ChoiceField']


def standard_validation_error(field,value):
    if value == nodata:
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
                 widget = None,
                 **kwargs):
        self.name = name
        self.default = default or self.default
        self.required = required
        self.validation_error = validation_error or standard_validation_error
        self.help_text = help_text
        self.label = label or self.name
        self.widget = widget
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
    
    def clean(self, value):
        if value == nodata or not value:
            if not required:
                default = self.default
                if hasattr(default,'__call__'):
                    default = default()
                return default
            else:
                raise ValidationError(self.validation_error(self,novalue))
        return self._clean(value)
    
    def _clean(self, value):
        return value
        
        
class CharField(Field):
    
    def _handle_params(self, max_length = 30, **kwargs):
        if not max_length:
            raise ValueError('max_length must be provided for {0}'.format(self.__class__.__name__))
        self.max_length = int(max_length)
        if self.max_length <= 0:
            raise ValueError('max_length must be positive')
        self._raise_error(kwargs)
        
    def _clean(self, value):
        try:
            return str(value)
        except:
            raise ValidationError


class IntegerField(Field):
    
    def _handle_params(self, validator = None, **kwargs):
        self.validator = validator
        self._raise_error(kwargs)
        
    def _clean(self, value):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError
        
        
class DateField(Field):
    
    def _clean(self, value):
        try:
            value = int(value)
            if self.validator:
                return self.validator(value)
            return value
        except:
            raise ValidationError
    
    
class ChoiceField(Field):
    
    def _handle_params(self, choices = None, **kwargs):
        self.choices = choices
        self._raise_error(kwargs)
    

to_implement = ['FloatField',
           'DateTimeField',
           'BooleanField',
           'CharField',
           'FileField',
           'RegexField',
           'EmailField',
           'ChoiceField',
           'LazyAjaxChoice',
           'ModelCharField',
           'SlugField']

