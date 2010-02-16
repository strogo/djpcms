from django import forms
from django.utils.importlib import import_module

from djpcms.views.appsite.options import ApplicationBase, ModelApplication
from djpcms.views.appsite.appsites import ApplicationSite, site
from djpcms.forms import LazyChoiceField
from djpcms.views.appsite.appurls import *


def load():
    '''
    Load dynamic applications and create urls
    '''
    from djpcms.settings import APPLICATION_URL_MODULE
    import djpcms.views.contentedit
    if APPLICATION_URL_MODULE:
        app_module = import_module(APPLICATION_URL_MODULE)
        

        

class ChangeForm(forms.ModelForm):
    application = LazyChoiceField(choices = site.choices)
        
    def save(self, commit = True):
        return super(ChangeForm,self).save(commit = commit)
