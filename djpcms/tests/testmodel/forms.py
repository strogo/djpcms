from django import forms
from django.forms.models import BaseModelFormSet

from djpcms.utils import uniforms
from djpcms.tests.testmodel.models import Strategy, StrategyTrade


class TradeForm(forms.ModelForm):
    name = forms.CharField(label = 'name')
    currency = forms.ChoiceField(choices=(('EUR','EUR'),('USD','USD')),
                                 label = 'currency')
    
    class Meta:
        exclude = ['trade']
        model = StrategyTrade


TradeForm = uniforms.ModelFormInlineHelper(Strategy,
                                           StrategyTrade,
                                           form = TradeForm,
                                           extra = 5)


class StrategyForm(forms.ModelForm):
    helper = uniforms.FormHelper()
    helper.inlines.append(TradeForm)
    
    class Meta:
        model = Strategy