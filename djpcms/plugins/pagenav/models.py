from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djpcms.models import DJPplugin

__all__ = ['PageNavigation']
    

class PageNavigation(DJPplugin):
        
    def __unicode__(self):
        if self.snippet:
            return u'Page Navigation'
        else:
            return u''
        
    def changeform(self, data = None, prefix = None):
        return ChangeForm(instance = self, prefix = prefix)
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''
        
    def render(self, request, prefix, wrapper, view = None):
        return view.page_navigation(request)

    
    
    