from django import forms
from django.utils.importlib import import_module

from djpcms.plugins.application.appsite.options import ModelApplication
from djpcms.plugins.application.appsite.appsites import ApplicationSite, site
from djpcms.plugins.application.models import DynamicApplication
from djpcms.forms import LazyChoiceField


def load():
    from djpcms.settings import APPLICATION_MODULE
    if APPLICATION_MODULE:
        app_module = import_module(APPLICATION_MODULE)
        
        

class ChangeForm(forms.ModelForm):
    application = LazyChoiceField(choices = site.choices)
    
    class Meta:
        model = DynamicApplication
        
    def save(self, commit = True):
        return super(ChangeForm,self).save(commit = commit)
