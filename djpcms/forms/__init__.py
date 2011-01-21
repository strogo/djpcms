from base import *
from fields import *




####### TO BE REMOVED
from widgets import *
from autocomplete import *
from utils import *

from django import forms
from django.forms import Media, MediaDefiningClass, BaseForm, ModelForm
from django.forms.forms import BoundField

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