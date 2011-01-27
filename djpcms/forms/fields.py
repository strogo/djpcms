from copy import copy, deepcopy

from djpcms import sites, nodata

from .globals import *
from .html import TextInput

__all__ = ['Field',
           'CharField',
           'BooleanField',
           'DateField',
           'ChoiceField',
           'IntegerField',
           'ModelChoiceField']


def standard_validation_error(field,value):
    if value == nodata:
        return 'Field {0} is required'.format(field.name)
    else:
        return str(value)
    

class Field(object):
    default = None
    widget = None
    creation_counter = 0
    
    def __init__(self,
                 required = True,
                 default = None,
                 validation_error = None,
                 help_text = None,
                 label = None,
                 widget = None,
                 **kwargs):
        self.name = None
        self.default = default or self.default
        self.required = required
        self.validation_error = validation_error or standard_validation_error
        self.help_text = help_text
        self.label = label
        self.widget = widget or self.widget
        self._handle_params(**kwargs)
        # Increase the creation counter, and save our local copy.
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        
    def set_name(self, name):
        self.name = name
        if not self.label:
            self.label = name
        
    def _handle_params(self, **kwargs):
        self._raise_error(kwargs)
        
    def _raise_error(self, kwargs):
        keys = list(kwargs)
        if keys:
            raise ValueError('Parameter {0} not recognized'.format(keys[0]))
    
    def clean(self, value, bfield):
        '''Clean the field value'''
        if value == nodata or not value:
            if not self.required:
                return self.get_default(bfield)
            else:
                value = self.get_default(bfield)
                if not value:
                    raise ValidationError(self.validation_error(self,nodata))
                return value
        return value
    
    def get_default(self, bfield):
        default = self.default
        if hasattr(default,'__call__'):
            default = default(bfield)
        return default
    
    def copy(self, bfield):
        result = copy(self)
        result.widget = deepcopy(self.widget)
        return result


class CharField(Field):
    default = ''
    widget = TextInput
    
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
    widget = TextInput
    
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
    widget = TextInput
    
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
        '''Choices is an iterable or a callable which takes the form as only argument'''
        self.choices = choices
        self._raise_error(kwargs)
        
    def clean(self, value, bfield):
        '''Clean the field value'''
        if value == nodata:
            ch = self.choices
            if not hasattr(ch,'__getitem__'):
                ch = list(ch)
                self.choices = ch
            if ch:
                value = ch[0][0]
                return value
        return super(ChoiceField,self).clean(value, bfield)
        
    def copy(self, bfield):
        ch = self.choices
        self.choices = None
        result = super(ChoiceField,self).copy(bfield)
        self.choices = ch
        if hasattr(ch,'__call__'):
            ch = ch(bfield)
        result.choices = ch
        return result
    
    
class BooleanField(Field):

    def _clean(self, value):
        """Returns a Python boolean object."""
        if value in ('False', '0'):
            value = False
        else:
            value = bool(value)
        return value
    
    
class ModelChoiceField(ChoiceField):
    pass

