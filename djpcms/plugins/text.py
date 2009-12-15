#
#
from django import forms
from django.conf import settings

from djpcms.utils import json
from djpcms.models import SiteContent
from djpcms.plugins import DJPplugin
from djpcms.forms import SlugField
from djpcms.utils import form_kwargs
from djpcms import markup


class NewContentCode(SlugField):
    
    def __init__(self, *args, **kwargs):
        super(NewContentCode,self).__init__(*args,**kwargs)
        
    def clean(self, value):
        return value
    
    def clean2(self, value):
        return super(NewContentCode,self).clean(value)


class ChangeTextContent(forms.Form):
    '''
    Form for changing text content during inline editing
    '''
    site_content = forms.ModelChoiceField(queryset = SiteContent.objects.all(),
                                          empty_label=u"New Content", required = False)
    new_content  = NewContentCode(SiteContent,
                                  'code',
                                  label = 'New content unique code',
                                  help_text = 'When creating a new content give a unique name you like',
                                  required = False)
    markup       = forms.ChoiceField(choices = markup.choices(),
                                     initial = markup.default(),
                                     required = False)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        initial = kwargs.pop('initial',None)
        if initial:
            site_content = initial.get('site_content',None)
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                initial['markup'] = site_content.markup
            except:
                pass
        kwargs['initial'] = initial
        self.user = request.user
        super(ChangeTextContent,self).__init__(*args,**kwargs)
        
    def clean_new_content(self):
        sc = self.cleaned_data['site_content']
        nc = self.cleaned_data['new_content']
        if not sc:
            if not nc:
                raise forms.ValidationError('New content name must be provided')
            avail = SiteContent.objects.filter(code = nc)
            if avail:
                raise forms.ValidationError('New content name already used')
        return nc
    
    def update(self):
        if self.is_valid():
            cd   = self.cleaned_data
            text = cd.get('site_content',None)
            nc   = cd.get('new_content',u'')
            # If new_content is available. A new SiteContent object is created
            if not text:
                text = SiteContent(code = nc)
            text.markup    = cd.get('markup')
            text.user_last = self.user
            text.save()
            return text
        


class EditContentForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        super(EditContentForm,self).__init__(*args,**kwargs)
        
    class Meta:
        model = SiteContent
        fields = ('body',)

    
class Text(DJPplugin):
    name          = "text"
    withrequest   = True
    form          = ChangeTextContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return u''
            
    def render(self, djp, wrapper, prefix, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return site_content.htmlbody()
            except Exception, e:
                if settings.DEBUG:
                    return u'%s' % e 
                else:
                    return u''
        else:
            return u''
    
    def edit_form(self, djp, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return EditContentForm(**form_kwargs(request = djp.request,
                                                     instance = site_content,
                                                     withrequest = True,
                                                     **kwargs))
            except Exception, e:
                return None
            
    def save(self, pform):
        text = pform.update()
        return json.dumps({'site_content': text.id})
        
        