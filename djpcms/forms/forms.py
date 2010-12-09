from djpcms.conf import settings

from django import forms
from django.forms.forms import get_declared_fields
from django.forms.widgets import media_property
from django.db import models
from django.forms.forms import BoundField

from djpcms.utils.html import ModelChoiceField, ModelMultipleChoiceField, submit


BaseForm = forms.BaseForm
ModelForm = forms.ModelForm
IntegerField = forms.IntegerField
FloatField = forms.FloatField
DateField = forms.DateField
DateTimeField = forms.DateTimeField
Select    = forms.Select
Textarea  = forms.Textarea
TextInput = forms.TextInput
BooleanField = forms.BooleanField
CharField = forms.CharField
ChoiceField = forms.ChoiceField
CheckboxInput = forms.CheckboxInput
FileField = forms.FileField
HiddenInput = forms.HiddenInput
RegexField = forms.RegexField
EmailField = forms.EmailField
PasswordInput = forms.PasswordInput
ValidationError = forms.ValidationError
model_to_dict = forms.model_to_dict
MediaDefiningClass = forms.MediaDefiningClass


class Form(forms.Form):
    '''A slight modification on django Form'''
    def __init__(self, *args, **kwargs):
        kwargs.pop('instance',None)
        self.request = kwargs.pop('request',None)
        super(Form,self).__init__(*args, **kwargs)


class ModelForm(forms.ModelForm):
    '''A slight modification on django Form'''
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request',None)
        super(ModelForm,self).__init__(*args, **kwargs)
        
        
def modelform_factory(model, form=ModelForm, **kwargs):
    from django.forms import models 
    return models.modelform_factory(model, form=form, **kwargs)

        
class LazyChoiceField(ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
        self._lazy_choices = kwargs.pop('choices',())
        super(LazyChoiceField,self).__init__(*args, **kwargs)
        
    def __deepcopy__(self, memo):
        result = super(LazyChoiceField,self).__deepcopy__(memo)
        lz = self._lazy_choices
        if callable(lz):
            lz = lz()
        result.choices = lz
        return result


class LazyAjaxChoice(LazyChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(LazyAjaxChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': settings.HTML_CLASSES.ajax}
    

class ModelCharField(CharField):
    
    def __init__(self, model, fieldname, extrafilters = None, *args, **kwargs):
        self.model       = model
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
    
