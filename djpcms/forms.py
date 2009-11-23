from django import forms
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djpcms.settings import HTML_CLASSES
from djpcms.models import Page, BlockContent, SiteContent
from djpcms.utils import lazyattr
from djpcms import siteapp_choices
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator


class LazyChoiceField(forms.ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
        # remove choices from kwargs.
        # choices should be an iterable
        self._lazy_choices = kwargs.pop('choices',())
        super(LazyChoiceField,self).__init__(*args, **kwargs)
        
    def __deepcopy__(self, memo):
        result = super(LazyChoiceField,self).__deepcopy__(memo)
        lz = self._lazy_choices
        if callable(lz):
            lz = lz()
        result.choices = lz
        return result


class LazyAjaxChoice(LazyChoiceField):
    
    def __init__(self, *args, **kwargs):
        super(LazyAjaxChoice,self).__init__(*args, **kwargs)
        
    def widget_attrs(self, widget):
        return {'class': HTML_CLASSES.ajax}
    

class ModelCharField(forms.CharField):
    
    def __init__(self, model, fieldname, extrafilters = None, *args, **kwargs):
        self.model       = model
        self.model_field = None
        for field in model._meta.fields:
            if field.attname == fieldname:
                self.model_field = field
                break
        if not self.model_field:
            raise ValueError('field %s not available in model %s' % (fieldname,model))
        if not isinstance(self.model_field,models.CharField):
            raise ValueError('field %s not char field in model %s' % (fieldname,model))
        self.extrafilters = extrafilters
        super(ModelCharField,self).__init__(*args, **kwargs)
        
    def clean(self, value):
        value = super(ModelCharField,self).clean(value)
        fieldname = self.model_field.attname
        try:
            value = value[:self.model_field.max_length]
        except:
            value = value
        value = self.trim(value)
        if self.model_field._unique:
            kwargs = self.extrafilters or {}
            kwargs[fieldname] = value
            obj = self.model.objects.filter(**kwargs)
            if obj.count():
                raise forms.ValidationError('%s code already available' % value)
        return value
        
    def trim(self, value):
        return value


class SlugField(ModelCharField):
    
    def __init__(self, *args, **kwargs):
        super(SlugField,self).__init__(*args, **kwargs)
        
    def trim(self, value):
        return self.model_field.trim(value)
    

# Form for a Page
class PageForm(forms.ModelForm):
    '''
    Page form
    This specialized form takes care of all the possible permutation
    in input values. These are the possibilities
        
        1) parent = None
            a) the unique root page
            b) an application page (application field must be available)
        2) 
    '''
    site        = forms.ModelChoiceField(queryset = Site.objects.all(), required = False)
    application = LazyChoiceField(choices = siteapp_choices,
                                  required = False,
                                  label = _('application'))
    
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
        '''
        Check for site
        '''
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
    
    def clean_application(self):
        '''
        If application type is specified, than it must be unique
        '''
        data = self.data
        app = data.get('application',None)
        if app:
            others = Page.objects.filter(application = app)
            for other in others:
                if other != self.instance:
                    raise forms.ValidationError('Application page %s already avaiable' % app)
        else:
            parent = self.get_parent()
            if not parent:
                # No parent specified. Let's check that a root is not available
                root = Page.objects.root()
                if root and root != self.instance:
                    raise forms.ValidationError('Page root already avaiable')
        return app
        
    def clean_url_pattern(self):
        '''
        Check for url patterns
            No need if:
                1 - it is the root page
                2 - oit is an application page
            Otherwise it is required
        '''
        data     = self.data
        value    = data.get('url_pattern',None)
        if value:
            return value
        app      = data.get('application',None)
        if app:
            return value
        parent   = data.get('parent',None)
        if parent:
            raise forms.ValidationError('url_pattern or application must be provided if not root page')
        return value
        
    def save(self, commit = True):
        return super(PageForm,self).save(commit)
        

class PluginChoice(LazyAjaxChoice):
    
    def __init__(self, *args, **kwargs):
        super(PluginChoice,self).__init__(*args, **kwargs)
    
    def clean(self, value):
        '''
        Overried default value to return a Content Type object
        '''
        name = super(PluginChoice,self).clean(value)
        value = get_plugin(name) 
        if not value:
            raise forms.ValidationError('%s not a plugin object' % name)
        return value
    

class ContentBlockForm(forms.ModelForm):
    '''
    Content Block Change form
    
    This Model form is used to change the plug-in within
    for a given BlockContent instance.
    '''
    plugin_name    = PluginChoice(label = _('content'),   choices = plugingenerator, required = False)
    container_type = LazyChoiceField(label=_('container'), choices = wrappergenerator)
    
    class Meta:
        model = BlockContent
        
    def __init__(self, instance = None, **kwargs):
        '''
        @param instance: must be an instance of BlockContent not Null
        '''
        if not instance:
            raise ValueError('No content block available')
        super(ContentBlockForm,self).__init__(instance = instance, **kwargs)
        # Hack the field ordering
        self.fields.keyOrder = ['plugin_name', 'container_type', 'title']
        
    def save(self, commit = True):
        pt = self.cleaned_data.pop('plugin_name')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        return super(ContentBlockForm,self).save(commit = commit)




AS_Q_CHOICES = (
    ('more:dev_docs', 'Latest'),
    ('more:1.0_docs', '1.0'),
    ('more:0.96_docs', '0.96'),
    ('more:all_docs', 'All'),
)

class SearchForm(forms.Form):
    q = forms.CharField(widget=forms.TextInput({'class': 'query'}))
    as_q = forms.ChoiceField(choices=AS_Q_CHOICES, widget=forms.RadioSelect, initial='more:dev_docs')


