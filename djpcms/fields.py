"""
A custom Model Field for djpcms.
"""
import copy

from django.conf import settings
from django.db.models.fields import CharField
from django import forms

from djpcms.utils.func import slugify

def get_ajax():
    from djpcms.settings import HTML_CLASSES
    return HTML_CLASSES



class SlugCode(CharField):
    
    def __init__(self, rtxchar='-', lower=False, upper = False, **kwargs):
        '''
        @param lower: boolean, if true the field will be converted to lower case
        @param upper: boolen if lower is False and this is True the field will be converted to upper cases 
        '''
        self.rtxchar = u'%s' % rtxchar
        self.lower   = lower
        self.upper   = upper
        super(SlugCode,self).__init__(**kwargs)
        
    def trim(self, value):
        value = slugify(u'%s'%value, rtx = self.rtxchar)
        if self.lower:
            value = value.lower()
        elif self.upper:
            value = value.upper()
        return value
        
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        value = self.trim(value)
        setattr(model_instance, self.attname, value)
        return value


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^djpcms\.fields\.SlugCode"])
except:
    pass