#
#
from django.template import RequestContext

from djpcms.conf import settings
from djpcms import forms
from djpcms.utils import json, form_kwargs, mark_safe
from djpcms.models import SiteContent
from djpcms.plugins import DJPplugin
from djpcms.utils.uniforms import FormLayout, Fieldset, blockLabels2, inlineLabels
from djpcms.markup import markuplib

from djpcms.utils import uniforms


class NewContentCode(forms.SlugField):
    
    def __init__(self, *args, **kwargs):
        super(NewContentCode,self).__init__(*args,**kwargs)
        
    def clean(self, value):
        return value
    
    def clean2(self, value):
        return super(NewContentCode,self).clean(value)


class SiteContentField(forms.ModelChoiceField):
    
    def widget_attrs(self, widget):
        return {'class': settings.HTML_CLASSES.ajax}


class ChangeTextContent(forms.Form):
    '''
    Form for changing text content during inline editing
    '''
    site_content = SiteContentField(queryset = SiteContent.objects.all(),
                                    empty_label=u"New Content",
                                    required = False)
    new_content  = NewContentCode(SiteContent,
                                  'code',
                                  label = 'New content unique code',
                                  help_text = 'When creating a new content give a unique name you like',
                                  required = False)
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
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
            text.user_last = self.user
            text.save()
            return text
        


class EditContentForm(forms.EditingForm):
    markup       = forms.LazyChoiceField(choices = markuplib.choices,
                                         initial = markuplib.default,
                                         required = False)
    
    layout = FormLayout(Fieldset('markup',css_class=inlineLabels),
                        Fieldset('body',css_class='%s editing' % blockLabels2))
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if not request:
            raise ValueError('Request not available')
        self.user = request.user
        super(EditContentForm,self).__init__(*args,**kwargs)
        
    class Meta:
        model = SiteContent
        fields = ('body','markup','url')

    
class Text(DJPplugin):
    '''The text plugin allows to write content in a straightforward manner.
You can use several different markup languages or simply raw HTML.'''
    name               = "text"
    description        = "Text Editor"
    long_description   = "Write text or raw HTML"
    form_withrequest   = True
    form               = ChangeTextContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return u''
            
    def render(self, djp, wrapper, prefix, site_content = None, **kwargs):
        if site_content:
            try:
                site_content = SiteContent.objects.get(id = int(site_content))
                return mark_safe('\n'.join(['<div class="djpcms-text-content">',
                                            site_content.htmlbody(),
                                            '</div>']))
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
                #return formlet(form = f, layout = 'djpcms/form/text-edit-form.html')
            except Exception, e:
                return None
            
    def save(self, pform):
        text = pform.update()
        return json.dumps({'site_content': text.id})
        


class HtmlContent(forms.Form):
    content = forms.CharField(label="HTML content", widget = forms.Textarea())
    layout = FormLayout(Fieldset('content',css_class=blockLabels2))

        
class Html(DJPplugin):
    '''Html plugin. Write what you like, javascript and HTML.'''
    name          = "html"
    description   = "HTML Snippet"
    form          = HtmlContent
    
    def html(self):
        if self.site_content:
            return self.site_content.bodyhtml()
        else:
            return u''
            
    def render(self, djp, wrapper, prefix, content = None, **kwargs):
        return u'' if  not content else mark_safe(content)
    