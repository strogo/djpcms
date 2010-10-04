from django import forms
from django.db import models
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djpcms.conf import settings
from djpcms.models import Page, BlockContent, SiteContent, create_page
from djpcms.utils import lazyattr
from djpcms import siteapp_choices
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator
from djpcms.utils.uniforms import FormLayout, Fieldset, Columns, Row, Html, inlineLabels
from djpcms.utils.html import ModelChoiceField, ModelMultipleChoiceField, submit


Form = forms.Form
Textarea = forms.Textarea
ModelForm = forms.ModelForm
BooleanField = forms.BooleanField
CharField = forms.CharField
ChoiceField = forms.ChoiceField
FileField = forms.FileField
ValidationError = forms.ValidationError
model_to_dict = forms.model_to_dict


class SearchForm(Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    search_text = CharField(required = False,
                            widget = forms.TextInput(attrs = {'class': 'sw_qbox autocomplete-off',
                                                              'title': 'Enter your search text'}))


class LazyChoiceField(ChoiceField):
    '''
    A Lazy ChoiceField.
    This ChoiceField does not unwind choices until a deepcopy is called on it.
    This allows for dynamic choices generation every time an instance of a Form is created.
    '''
    def __init__(self, *args, **kwargs):
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
        return {'class': settings.HTML_CLASSES.ajax}
    

class ModelCharField(CharField):
    
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
class PageForm(ModelForm):
    '''
    Page form
    This specialized form takes care of all the possible permutation
    in input values. These are the possibilities
        
        1) parent = None
            a) the unique root page
            b) an application page (application field must be available)
        2) 
    '''
    site        = ModelChoiceField(queryset = Site.objects.all(), required = False)
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
        
    @lazyattr
    def clean_site(self):
        '''
        Check for site.
        If site not provided and the parent page is available, we return the parent page site.
        Otherwise we return the currenct site.
        '''
        site   = self.cleaned_data.get('site',None)
        parent = self.get_parent()
        if not site:
            if not parent:
                return Site.objects.get_current()
            else:
                return parent.site
        elif parent:
            return parent.site
        else:
            return site
    
    def clean_application(self):
        '''If application type is specified, than it must be unique
        '''
        from djpcms.views import appsite
        data = self.data
        app = data.get('application',None)
        if app:
            try:
                application = appsite.site.getapp(app)
            except KeyError:
                raise forms.ValidationError('Application %s not available' % app)
            parent = self.get_parent()
            bit = data.get('url_pattern','')
            if not application.regex.names:
                data['url_pattern'] = ''
                bit = ''
            others = Page.objects.filter(application = application.code,
                                         site = self.clean_site(),
                                         url_pattern = bit)
            for other in others:
                if other != self.instance:
                    raise forms.ValidationError('Application page %s already avaiable' % app)
        else:
            parent = self.get_parent()
            if not parent:
                # No parent specified. Let's check that a root is not available
                root = Page.objects.root(self.clean_site())
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
    
    
class EditingForm(ModelForm):
    url  = CharField(widget=forms.HiddenInput, required = False)
    
    

class ContentBlockForm(EditingForm):
    '''Content Block Change form
    
    This Model form is used to change the plug-in within
    for a given BlockContent instance.
    '''
    plugin_name    = PluginChoice(label = _('Plugin'),   choices = plugingenerator, required = False)
    container_type = LazyChoiceField(label=_('Container'), choices = wrappergenerator)
    
    class Meta:
        model = BlockContent
        fields = ['plugin_name','container_type','title','url']
        
    def __init__(self, instance = None, **kwargs):
        '''
        @param instance: must be an instance of BlockContent not Null
        '''
        if not instance:
            raise ValueError('No content block available')
        super(ContentBlockForm,self).__init__(instance = instance, **kwargs)
        # Hack the field ordering
        #self.fields.keyOrder = ['plugin_name', 'container_type', 'title']
        
    def save(self, commit = True):
        pt = self.cleaned_data.pop('plugin_name')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        return super(ContentBlockForm,self).save(commit = commit)



# Short Form for a Page
class ShortPageForm(ModelForm):
    '''Form to used to edit inline a page'''
    layout = FormLayout(Columns(('title','parent','inner_template','in_navigation'),
                                ('link','url_pattern','cssinfo',Row('soft_root','requires_login')))
                        )
    
    class Meta:
        model = Page
        fields = ['link','title','inner_template','url_pattern','cssinfo',
                  'in_navigation','requires_login','soft_root',
                  'parent']


class NewChildForm(Form):
    child  = CharField(label = 'New child page url', required = True)
    layout = FormLayout(Fieldset('child', css_class = inlineLabels))
    
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response',None)
        super(NewChildForm,self).__init__(*args, **kwargs)
    
    def clean_child(self):
        name = self.cleaned_data.get('child',None)
        if name and self.response:
            child = self.response.page.children.filter(url_pattern = name)
            if child:
                raise Form.ValidationError('child page %s already available' % name)
        return name
    
    def save(self):
        djp    = self.response
        parent = djp.page
        url    = self.cleaned_data['child']
        return create_page(url, parent = parent, user = parent.user)

