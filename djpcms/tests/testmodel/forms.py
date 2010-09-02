from django import forms

from djpcms.utils import uniforms
from djpcms.tests.testmodel.models import Strategy



class StrategyForm(forms.ModelForm):
    helper = uniforms.FormHelper()
    
    class Meta:
        model = Strategy