#
#
from django import forms

from djpcms.models import SiteContent
from djpcms.plugins import DJPplugin
from djpcms.forms import SlugField
from djpcms.utils.markups import markup_choices, default_markup


class NewContentCode(SlugField):
    
    def __init__(self, *args, **kwargs):
        super(NewContentCode,self).__init__(*args,**kwargs)
        
    def clean(self, value):
        return value
    
    def clean2(self, value):
        return super(NewContentCode,self).clean(value)


class ChangeTextContent(forms.Form):
    site_content = forms.ModelChoiceField(queryset = SiteContent.objects.all(),
                                          empty_label=u"New Content", required = False)
    new_content  = NewContentCode(SiteContent,
                                  'code',
                                  label = 'New content unique code',
                                  help_text = 'When creating a new content give a unique name you like',
                                  required = False)
    markup       = forms.ChoiceField(choices = markup_choices(),
                                     initial = default_markup,
                                     required = False)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        super(ChangeTextContent,self).__init__(*args,**kwargs)
        
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
    


class Text(DJPplugin):
    withrequest = True
    form        = ChangeTextContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return u''
            
    def render(self, djp, wrapper, prefix, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return self.site_content.htmlbody()
            except:
                return u''
        else:
            return u''
    
    