from django import forms
from django.db import models


from djpcms.models import DJPplugin, SiteContent
from djpcms.djutils import form_kwargs
from djpcms.djutils.fields import SlugField
from djpcms.markups import markup_choices, default_markup

__all__ = ['TextEditor']



class TextEditor(DJPplugin):
    site_content  = models.ForeignKey(SiteContent, null = True, verbose_name = 'content')
    
    class Meta:
        ordering  = ('site_content',)
        verbose_name = 'Text Editor'
        
    def __unicode__(self):
        b = super(TextEditor,self).__unicode__()
        if self.site_content:
            return u'%s: %s' % (b,self.site_content.code)
        else:
            return b
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return u''
            
    def render(self, request, prefix, wrapper, **kwargs):
        if self.site_content:
            return self.site_content.htmlbody()
        else:
            return u''
        
    def changeform(self, request = None, prefix = None):
        return ChangeForm(**form_kwargs(request, instance = self, prefix = prefix, withrequest = True))



class NewContentCode(SlugField):
    
    def __init__(self, *args, **kwargs):
        super(NewContentCode,self).__init__(*args,**kwargs)
        
    def clean(self, value):
        return value
    
    def clean2(self, value):
        return super(NewContentCode,self).clean(value)



class ChangeForm(forms.ModelForm):
    site_content = forms.ModelChoiceField(queryset = SiteContent.objects.all(), empty_label=u"New Content", required = False)
    new_content  = NewContentCode(SiteContent,
                                  'code',
                                  label = 'New content unique code',
                                  help_text = 'When creating a new content give a unique name you like',
                                  required = False)
    markup       = forms.ChoiceField(choices = markup_choices(),
                                     initial = default_markup,
                                     required = False)
    
    class Meta:
        model = TextEditor
        
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        super(ChangeForm,self).__init__(*args,**kwargs)
        
    def clean_new_content(self):
        sc = self.cleaned_data.get('site_content',None)
        nc = self.cleaned_data.get('new_content',u'')
        if not sc and not nc:
            raise forms.ValidationError('New content title must be provided')
        if nc:
            return self.fields['new_content'].clean2(nc)
        else:
            return nc
    
    def save(self, commit = True):
        nc = self.cleaned_data.get('new_content',u'')
        # If new_content is available. A new SiteContent object is created
        if nc:
            self.instance = SiteContent(code = nc)
        self.instance.user_last = self.user
        return super(ChangeForm,self).save(commit)
            
    