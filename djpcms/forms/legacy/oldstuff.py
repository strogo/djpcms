
####### TO BE REMOVED
from widgets import *
from autocomplete import *
from utils import *

from django import forms
from django.forms import Media, MediaDefiningClass, BaseForm, ModelForm
from django.forms.forms import BoundField
from django.db import models

model_to_dict = forms.model_to_dict
OldCharField = forms.CharField
OldIntegerField = forms.IntegerField
OldBooleanField = forms.BooleanField
OldBooleanField = forms.BooleanField
EmailField = forms.EmailField
RegexField = forms.RegexField


class OldChoiceField(forms.ChoiceField):
    '''
A Lazy ChoiceField.
This ChoiceField does not unwind choices until a deepcopy is called on it.
This allows for dynamic choices generation every time an instance of a Form is created.
'''
    def __init__(self, *args, **kwargs):
        self._lazy_choices = kwargs.pop('choices',())
        super(OldChoiceField,self).__init__(*args, **kwargs)
        
    def __deepcopy__(self, memo):
        result = super(ChoiceField,self).__deepcopy__(memo)
        lz = self._lazy_choices
        if callable(lz):
            lz = lz()
        result.choices = lz
        return result
   
    
class LazyAjaxChoice(OldChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(LazyAjaxChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': sites.settings.HTML_CLASSES.ajax}
    
    
class ModelCharField(OldCharField):
    
    def __init__(self, model, fieldname, extrafilters = None, *args, **kwargs):
        self.model = model
        self.model_field = None
        for field in model._meta.fields:
            if field.attname == fieldname:
                self.model_field = field
                break
        if not self.model_field:
            raise ValueError('field %s not available in model %s' % (fieldname,model))
        if not isinstance(self.model_field,models.CharField):
            raise ValueError('field %s not char field in model %s' % (fieldname,model))
        self.extrafilters = extrafilters
        super(ModelCharField,self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = super(ModelCharField,self).clean(value)
        fieldname = self.model_field.attname
        try:
            value = value[:self.model_field.max_length]
        except:
            value = value
        value = self.trim(value)
        if self.model_field._unique:
            kwargs = self.extrafilters or {}
            kwargs[fieldname] = value
            obj = self.model.objects.filter(**kwargs)
            if obj.count():
                raise forms.ValidationError('%s code already available' % value)
        return value
        
    def trim(self, value):
        return value
    
    
class SlugField(ModelCharField):
    
    def __init__(self, *args, **kwargs):
        super(SlugField,self).__init__(*args, **kwargs)
        
    def trim(self, value):
        return self.model_field.trim(value)