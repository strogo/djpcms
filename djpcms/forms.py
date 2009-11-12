from django import forms
from django.contrib.sites.models import Site

from djpcms.models import Page, AppPage
from djpcms.utils import lazyattr
from djpcms.plugins.application import appsite
from djpcms.djutils.fields import LazyChoiceField


class PageForm(forms.ModelForm):
    '''
    Page form
    This specialized form taks care of all th possible permutation
    in input values.
    '''
    site        = forms.ModelChoiceField(queryset = Site.objects.all(), required = False)
    code        = forms.CharField(max_length=32, required = False)
    url_pattern = forms.CharField(required = False)
    
    class Meta:
        model = Page
        
    @lazyattr
    def get_parent(self):
        pid = self.data.get('parent',None)
        if pid:
            return Page.objects.get(id = int(pid))
        else:
            return None
        
    def clean_code(self):
        parent = self.get_parent()
        app_type = self.data.get('app_type',None)
        if parent and app_type:
            return u'%s_%s' % (parent.code,app_type)
        else:
            code = self.data.get('code',None)
            if not code:
                raise forms.ValidationError('Code must be specified')
            return code
        
    def clean_site(self):
        data   = self.data
        site   = data.get('site',None)
        parent = self.get_parent()
        if not site:
            if not parent:
                raise forms.ValidationError('Either site or parent must be specified')
            return parent.site
        elif parent:
            return parent.site
        else:
            return Site.objects.get(id = int(site))
    
    def clean_app_type(self):
        '''
        If application type is specified,
        than a parent page with a content type must be available
        '''
        data = self.data
        app_type = data.get('app_type',None)
        if app_type:
            parent = self.get_parent()
            if parent:
                if parent.content_type:
                    return app_type
                else:
                    raise forms.ValidationError('Parent page with no content type')
            else:
                raise forms.ValidationError('App Type must have a parent page')
        else:
            return app_type
        
    def clean_url_pattern(self):
        data = self.data
        url = data.get('url_pattern',None)
        app_name = data.get('app_type',None)
        if app_name:
            data['url_pattern'] = u''
            return u''
        elif not url:
            raise forms.ValidationError('url_pattern or app_type must be provided')
        else:
            return url
        
    def save(self, commit = True):
        return super(PageForm,self).save(commit)
        
        
        
class AppPageForm(forms.ModelForm):
    code = LazyChoiceField(choices = appsite.site.choices, required = True, label = 'application')
    
    class Meta:
        model = AppPage
        

AS_Q_CHOICES = (
    ('more:dev_docs', 'Latest'),
    ('more:1.0_docs', '1.0'),
    ('more:0.96_docs', '0.96'),
    ('more:all_docs', 'All'),
)

class SearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput({'class': 'query'}))
    as_q = forms.ChoiceField(choices=AS_Q_CHOICES, widget=forms.RadioSelect, initial='more:dev_docs')
