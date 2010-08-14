from django import forms
from django.utils.importlib import import_module

from djpcms.views.appsite.appsites import ApplicationBase, ModelApplication, ApplicationSite, site
from djpcms.forms import LazyChoiceField


def load():
    '''Load dynamic applications and create urls
    '''
    from djpcms.conf import settings
    import djpcms.views.contentedit
    if settings.APPLICATION_URL_MODULE:
        app_module = import_module(settings.APPLICATION_URL_MODULE)
        


class ChangeForm(forms.ModelForm):
    application = LazyChoiceField(choices = site.choices)
        
    def save(self, commit = True):
        return super(ChangeForm,self).save(commit = commit)
