from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from djpcms import get_site, forms
from djpcms.utils import force_str, slugify
from djpcms.models import Page, BlockContent, SiteContent, ObjectPermission
from djpcms.utils.uniforms import FormLayout, Fieldset, Columns, Row, Html, inlineLabels, inlineLabels3
from djpcms.plugins import get_plugin, plugingenerator, wrappergenerator



def siteapp_choices():
    return get_site().choices


def CalculatePageUrl(data, page):
    '''Calculate url for a page'''
    site = get_site()
    application_view = data.get('application_view','')
    url_pattern  = data.get('url_pattern','')
    parent = data['parent']
    website = data['site']
    if application_view:
        app = site.getapp(application_view)
        if not app:
            raise ValueError("Application view %s not available on site." % application_view)
        data['application_view'] = app.code
        page.application = app.appmodel.name
        purl = app.urlbit.url
        if app.isroot():
            url  = app.baseurl
            root = Page.objects.filter(site = website, level = 0)
            if url == '/':
                if root:
                    root = root[0]
                    if root != page:
                        raise forms.ValidationError("Root page already available, cannot set application as root. Delete the flat root page first")
                parent = None
            else:
                url  = url[1:-1]
                urls = url.split('/')
                if len(urls) > 1:
                    url     = urls[-1]
                    parent_url = '/%s/' % '/'.join(urls[:-1])
                    root    = Page.objects.filter(site = website, url = parent_url)
                else:
                    parent_url = '/'
                    
                if root:
                    parent = root[0]
                else:
                    raise forms.ValidationError('Parent page "%s" not available, cannot set application %s' % (parent_url,application_view))
        else:
            if not parent:
                pages = Page.objects.filter(application_view = app.parent.code,
                                            site = website,
                                            url_pattern = '')
                if pages.count() == 1:
                    parent = pages[0]
                else:
                    raise forms.ValidationError('Parent page not defined for %s' % app.code)
            
            bit = url_pattern
            if bit and app.regex.names and parent.url_pattern != bit:
                bits = bit.split('/')
                kwargs = dict(zip(app.regex.names,bits))
                purl = app.regex.get_url(**kwargs)
            url = purl
    else:
        page.application = ''
        url = url_pattern
    
    data['parent'] = parent
    if parent:
        url = '%s%s' % (parent.url,url)
    if not url.endswith('/'):
        url += '/'
    if not url.startswith('/'):
        url = '/%s' % url
    return url
    
    

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
    site             = forms.ModelChoiceField(queryset = Site.objects.all(), required = False)
    application_view = forms.ChoiceField(choices = siteapp_choices,
                                         required = False,
                                         label = _('application view'))
    
    class Meta:
        model = Page
        exclude = ['application']
        
    def get_parent(self):
        pid = self.data.get('parent',None)
        if pid:
            return Page.objects.get(id = int(pid))
        else:
            return None
    
    def clean_application_view(self):
        '''If application type is specified, than it must be unique
        '''
        site = get_site()
        data = self.data
        app = data.get('application_view',None)
        if app:
            try:
                application_view = site.getapp(app)
            except KeyError:
                raise forms.ValidationError('Application view %s not available' % app)
            parent = self.get_parent()
            # Parent page is available
            if parent:
                if not application_view.parent:
                    parent = None
                    self.data.pop('parent',None)
                elif application_view.parent.code != parent.application_view:
                    raise forms.ValidationError("Page %s is not a parent of %s" % (parent,application_view))
            
            bit = data.get('url_pattern','')
            if not application_view.regex.names:
                data['url_pattern'] = ''
                bit = ''
            elif parent and application_view.parent:
                if parent.application_view == application_view.parent.code and parent.url_pattern:
                    bit = parent.url_pattern
                    data['url_pattern'] = bit
            others = Page.objects.filter(application_view = application_view.code,
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
            value = slugify(force_str(value))
        if data.get('application_view',None):
            return value
        parent = self.get_parent()
        if parent:
            if not value:
                raise forms.ValidationError('url_pattern or application view must be provided if not a root page')
            page = parent.children.filter(url_pattern = value)
            if page and page[0].id != self.instance.id:
                raise forms.ValidationError("page %s already available" % page)
        return value
        
    def clean(self):
        cd = self.cleaned_data
        site = cd['site']
        url = CalculatePageUrl(cd,self.instance)
        pages = Page.objects.filter(url = url, site = site)
        if pages:
            page = pages[0]
            if self.instance != page:
                raise forms.ValidationError('Page with url %s already in stitemap for site %s.' % (url,site))
        self.instance.url = url
        return cd
        

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
                                   choices = plugingenerator)
    container_type  = forms.ChoiceField(label=_('Container'), choices = wrappergenerator)
    view_permission = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required = False)
    layout = FormLayout(Fieldset('plugin_name','container_type','title','view_permission'),
                        Columns(('for_not_authenticated',),('requires_login',), css_class=inlineLabels3))
    
    class Meta:
        model = BlockContent
        fields = ['plugin_name','container_type','title','for_not_authenticated','requires_login']
        
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


# Short Form for a Page. Used only for editing an existing page
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
        
    submits = (('change', '_save'),)


class NewChildForm(forms.ModelForm):
    url_pattern = forms.CharField(label = 'New child page url', required = True)
    
    layout = FormLayout(Fieldset('url_pattern', css_class = inlineLabels))
    
    submits = (('create', '_child'),)
    
    class Meta:
        model = Page
        fields = ['soft_root','in_navigation','requires_login','inner_template']
    
    def clean_url_pattern(self):
        parent = self.instance
        if not parent.id:
            raise forms.ValidationError('Parent page not available')
        name = self.cleaned_data.get('url_pattern',None)
        child = parent.children.filter(url_pattern = name)
        if child:
            raise forms.ValidationError('child page %s already available' % name)
        return name
    
    def clean(self):
        cd = self.cleaned_data
        self.page_form = create_page(parent = self.instance, commit = False, **cd)
        return cd
    
    def save(self, commit = True):
        return self.page_form.save()

def ferrors(errdict):
    for el in errdict.itervalues():
        for e in el:
            yield e



def _getid(obj):
    if obj:
        try:
            return obj.id
        except:
            return obj
    else:
        return obj
        

def create_page(parent = None, user = None, inner_template = None, commit = True, **kwargs):
    '''Shortcut function for creating pages'''
    form = PageForm()
    data = forms.model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
    data.update(**kwargs)
    user = _getid(user)
    if parent:
        if not user:
            user = parent.user
        if not inner_template:
            inner_template = parent.inner_template
        parent = parent.id
    inner_template = _getid(inner_template)
    data.update({'parent':parent,'user':user, 'inner_template': inner_template})
    f = PageForm(data = data)
    if f.is_valid():
        if commit:
            return f.save(commit = commit)
        else:
            return f
    else:
        err = ' '.join(ferrors(f._errors))
        raise forms.ValidationError(err)
    
