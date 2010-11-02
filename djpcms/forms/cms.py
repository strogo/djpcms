from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djpcms import siteapp_choices
from djpcms.utils import smart_unicode
from djpcms.models import Page, BlockContent, SiteContent, ObjectPermission, create_page
from djpcms.utils.uniforms import FormLayout, Fieldset, Columns, Row, Html, inlineLabels, inlineLabels3
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator
from djpcms.utils.func import slugify

import forms



class SearchForm(forms.Form):
    '''
    A simple search form used by plugins.apps.SearchBox.
    The search_text name will be used by SearchViews to handle text search
    '''
    search_text = forms.CharField(required = False,
                                  widget = forms.TextInput(attrs = {'class': 'sw_qbox autocomplete-off',
                                                              'title': 'Enter your search text'}))
    

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
    application = forms.LazyChoiceField(choices = siteapp_choices,
                                        required = False,
                                        label = _('application'))
    
    class Meta:
        model = Page
        
    def get_parent(self):
        pid = self.data.get('parent',None)
        if pid:
            return Page.objects.get(id = int(pid))
        else:
            return None
    
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
            # Parent page is available
            if parent:
                if not application.parent:
                    parent = None
                    self.data.pop('parent',None)
                elif application.parent.code != parent.application:
                    raise forms.ValidationError("Page %s is not a parent of %s" % (parent,application))
            
            bit = data.get('url_pattern','')
            if not application.regex.names:
                data['url_pattern'] = ''
                bit = ''
            elif parent and application.parent:
                if parent.application == application.parent.code and parent.url_pattern:
                    bit = parent.url_pattern
                    data['url_pattern'] = bit
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
                    # We assume the page to be child of root. Lets check it is not already avialble
                    self.data['parent'] = root.id
                    #raise forms.ValidationError('Page root already avaiable')
        return app
    
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
            value = slugify(smart_unicode(value))
        if data.get('application',None):
            return value
        parent = self.get_parent()
        if parent:
            if not value:
                raise forms.ValidationError('url_pattern or application must be provided if not root page')
            page = parent.children.filter(url_pattern = value)
            if page and page[0].id != self.instance.id:
                raise forms.ValidationError("page %s already available" % page)
        return value
        
        
    def save(self, commit = True):
        return super(PageForm,self).save(commit)
        

class PluginChoice(forms.LazyAjaxChoice):
    
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
    
    
class EditingForm(forms.ModelForm):
    url  = forms.CharField(widget=forms.HiddenInput, required = False)
    
    

class ContentBlockForm(EditingForm):
    '''Content Block Change form
    
    This Model form is used to change the plug-in within
    for a given BlockContent instance.
    '''
    plugin_name     = PluginChoice(label = _('Plugin'),
                                   choices = plugingenerator,
                                   required = False)
    container_type  = forms.LazyChoiceField(label=_('Container'), choices = wrappergenerator)
    view_permission = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)
    layout = FormLayout(Fieldset('plugin_name','container_type','title','view_permission'),
                        Columns(('for_not_authenticated',),('requires_login',), css_class=inlineLabels3))
    
    class Meta:
        model = BlockContent
        fields = ['plugin_name','container_type','title','for_not_authenticated','requires_login']
        
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
        pe = self.cleaned_data.pop('view_permission')
        instance = self.instance
        if pt:
            instance.plugin_name = pt.name
        else:
            instance.plugin_name = ''
        if pe:
            instance.requires_login = True
        cb = super(ContentBlockForm,self).save(commit = commit)
        if cb.pk:
            ObjectPermission.objects.set_view_permission(cb, groups = pe)
        return cb

    def clean_requires_login(self):
        rl = self.cleaned_data['requires_login']
        if rl and self.cleaned_data['for_not_authenticated']:
            raise ValidationError("Select this or for not authenticated or neither. Cannot select both.")
        return rl
    
    def clean_view_permission(self):
        vp = self.cleaned_data['view_permission']
        if vp and self.cleaned_data['for_not_authenticated']:
            raise ValidationError("Select this or for not authenticated or neither. Cannot select both.")
        return vp


# Short Form for a Page
class ShortPageForm(forms.ModelForm):
    '''Form to used to edit inline a page'''
    view_permission = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)
    
    layout = FormLayout(Columns(('title','inner_template','in_navigation','requires_login'),
                                ('link','cssinfo','soft_root','view_permission'))
                        )
    def save(self, commit = True):
        pe = self.cleaned_data.pop('view_permission')
        page = super(ShortPageForm,self).save(commit)
        if page.pk:
            ObjectPermission.objects.set_view_permission(page, groups = pe)
        return page
    
    class Meta:
        model = Page
        fields = ['link','title','inner_template','cssinfo',
                  'in_navigation','requires_login','soft_root']


class NewChildForm(forms.Form):
    child  = forms.CharField(label = 'New child page url', required = True)
    
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


