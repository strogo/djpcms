from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template import Template, RequestContext

from djpcms.models import DJPplugin
from djpcms.djutils import form_kwargs

__all__ = ['SnippetPtr','Snippet']


class Snippet(models.Model):
    """
    A snippet of HTML or a Django template
    """
    name     = models.CharField(_("name"), max_length=255, unique=True)
    template = models.TextField(_("template"), blank = True)

    class Meta:
        ordering = ['name']
    
    def __unicode__(self):
        return self.name
    
    

class SnippetPtr(DJPplugin):
    snippet  = models.ForeignKey(Snippet, null = True)
    
    class Meta:
        ordering  = ('snippet',)
        verbose_name = 'HTML Snippet'
        
    def __unicode__(self):
        if self.snippet:
            return u'%s' % self.snippet
        else:
            return u''
        
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return ''
        
    def render(self, request, prefix, wrapper, view):
        '''
        Handle a request
        '''
        if self.snippet:
            t = Template(self.snippet.template)
            c = {'cl': view.requestview(request),
                 'prefix':prefix}
            return t.render(RequestContext(request,c))
        else:
            return u''
                
    def changeform(self, request = None, prefix = None):
        return ChangeForm(**form_kwargs(request, instance = self, prefix = prefix))



class ChangeForm(forms.ModelForm):
    class Meta:
        model = SnippetPtr
    
    
    