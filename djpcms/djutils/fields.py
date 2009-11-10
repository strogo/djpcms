import copy

from django.conf import settings
from django.db import models
from django import forms

from func import slugify


class SlugCode(models.CharField):
    
    def __init__(self, rtxchar='-', lower=False, upper = False, **kwargs):
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
    
    #def south_field_triple(self):
    #    "Returns a suitable description of this field for South."
    #    # We'll just introspect ourselves, since we inherit.
    #    from south.modelsinspector import introspector
    #    field_class = "django.db.models.fields.CharField"
    #    args, kwargs = introspector(self)
    #    return (field_class, args, kwargs)


    
    

class ModelCharField(forms.CharField):
    
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
    
    
    
class LazyChoiceField(forms.ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
        # remove choices from kwargs.
        # choices should be an iterable
        choices = kwargs.pop('choices',())
        super(LazyChoiceField,self).__init__(*args, **kwargs)
        self._lazy_choices = choices
        
    def __deepcopy__(self, memo):
        result = super(LazyChoiceField,self).__deepcopy__(memo)
        result.choices = self._lazy_choices
        return result
    
class LazyModelChoiceField(forms.ModelChoiceField):
    '''
    A Lazy ModelChoiceField.
    This ModelChoiceField does not unwind queryset until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
        # remove choices from kwargs.
        # choices should be an iterable
        #choices = kwargs.pop('queryset',())
        super(LazyModelChoiceField,self).__init__(*args, **kwargs)
        #self._lazy_choices = choices
        
    #def __deepcopy__(self, memo):
    #    result = super(LazyChoiceField,self).__deepcopy__(memo)
    #    result.choices = self._lazy_choices
    #    return result
    
        

_registered = False

if 'south' in settings.INSTALLED_APPS and not _registered:
    import _south
    _registered = True
