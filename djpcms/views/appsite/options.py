'''
Application Model Manager
This module define the base class for implementing Dynamic Page views based on django models
The main object handle several subviews used for searching, adding and manipulating objects
'''
from copy import deepcopy

from django import forms
from django.forms.models import modelform_factory
from django.utils.encoding import force_unicode
from django.utils.datastructures import SortedDict
from django.template import loader, Template, Context, RequestContext
from django.core.exceptions import PermissionDenied

from djpcms.utils import form_kwargs, UnicodeObject
from djpcms.utils.forms import add_hidden_field
from djpcms.plugins import register_application
from djpcms.views.baseview import editview
from djpcms.views.appview import AppView
from djpcms.settings import HTML_CLASSES

from djpcms.utils.html import formlet, submit, form


class SearchForm(forms.Form):
    '''
    A simple search box
    '''
    search = forms.CharField(max_length=300, required = False,
                             widget = forms.TextInput(attrs={'class':'search-box'}))
    

class ModelApplicationUrlError(Exception):
    pass

def get_declared_applications(bases, attrs):
    """
    Create a list of ModelApplication children instances from the passed in 'attrs', plus any
    similar fields on the base classes (in 'bases').
    """
    inherit = attrs.pop('inherit',False)
    apps = [(app_name, attrs.pop(app_name)) for app_name, obj in attrs.items() if isinstance(obj, AppView)]      
    apps.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    # If this class is subclassing another Application, and inherit is True add that Application's views.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if inherit:
        for base in bases[::-1]:
            if hasattr(base, 'base_applications'):
                apps = base.base_applications.items() + apps

    return SortedDict(apps)

class ModelAppMetaClass(type):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_applications'] = get_declared_applications(bases, attrs)
        new_class = super(ModelAppMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class
    


class ModelApplicationBase(object):
    '''
    Base class for model applications
    This class implements the basic functionality for a general model
    User should subclass this for full control on the model application.
    Each one of the class attributes are optionals
    '''
    ajax             = HTML_CLASSES
    # Name for this application. Optional (the model name will be used if None)
    name             = None
    # Base URL for the application including trailing slashes. Optional
    baseurl          = '/'
    # Does require authenticated user?
    autheinticated   = True
    # Form used for adding/editing objects.
    # This can be overritten with a function
    form             = forms.ModelForm
    # Form layout.
    form_layout      = None
    # Whether the form requires the request object to be passed to the constructor
    form_withrequest = False
    # Form response method, POST by default
    form_method      ='post'
    # if True add/edit/delete will be performed via AJAX xhr POST requests
    form_ajax        = True
    search_form      = None
    date_code        = None
    search_form      = SearchForm
    search_item_template = '''<div>{{ item }}</div>'''
    # Number of arguments to create an instance of model
    num_obj_args     = 1
    # True if applications can go into navigation
    in_navigation    = True
    # If set to True, base class views will be available
    inherit          = False
    # True is application is added in sitemap
    insitemap        = False
    
    def __init__(self, model, application_site, editavailable):
        self.model = model
        self.opts  = model._meta
        self.root_application = None
        self.application_site = application_site
        self.editavailable    = editavailable
        self.name             = self.name or self.opts.module_name
        if not self.baseurl:
            raise ModelApplicationUrlError('Base url for application %s not defined' % model)
        self.applications     = deepcopy(self.base_applications)
        self.edits            = []
        parent_url            = '/'.join(self.baseurl[1:-1].split('/')[:-1])
        if not parent_url:
            parent_url = '/'
        else:
            parent_url = '/%s/' % parent_url
        self.parent_url = parent_url
        parents = self.application_site.parent_pages
        children = parents.get(self.parent_url,None)
        if not children:
            children = []
            parents[self.parent_url] = children
        children.append(self)
        self.create_applications()
        
    def create_applications(self):
        roots = []
        for app_name,child in self.applications.items():
            child.name = app_name
            pkey       = child.parent
            if pkey:
                parent  = self.applications.get(pkey,None)
                if not parent:
                    raise ModelApplicationUrlError('Parent %s for %s not in children tree' % (pkey,child))
                child.parent = parent
            else:
                if not child.urlbit:
                    self.root_application = child
                else:
                    roots.append(child)
            child.processurlbits(self)
            code = u'%s-%s' % (self.name,child.name)
            child.code = code
            if child.isapp:
                name = u'%s %s' % (self.name,child.name.replace('_',' '))
                self.application_site.choices.append((code,name))
            if child.isplugin:
                register_application(child)
        #
        # Check for parents
        if len(roots) > 1:
            #TODO. Authomatic parent selections
            if self.root_application:
                for app in roots:
                    app.parent = self.root_application
                                
                
    def get_view_name(self, name):
        if not self.baseurl:
            raise ModelApplicationUrlError('Application without baseurl')
        base = self.baseurl[1:-1].replace('/','_')
        return '%s_%s' % (base,name)
        
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        return {'id': obj.id}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            id = int(kwargs.get('id',None))
            return self.model.objects.get(id = id)
        except:
            return None
        
    def get_baseurl(self):
        if self.baseurl:
            return self.baseurl
        else:
            return '/%s/' % self.name
    
    def getapp(self, code):
        return self.applications.get(code, None)
    
    def update_initial(self, request, mform, initial = None):
        if request.method == 'GET' and request.GET:
            params = dict(request.GET.items())
            next   = params.get('next')
            if next:
                mform = add_hidden_field(mform,'next')
                initial = initial or {}
                initial['next'] = next
        return initial
                
    def get_form(self, djp, prefix = None, initial = None, wrapped = True):
        '''
        Build an add/edit form for the application model
        @param djp: instance of djpcms.views.DjpRequestWrap 
        @param request: django HttpRequest instance
        @param instance: instance of self.model or None
        @param prefix: prefix to use in the form
        @param wrapper: instance of djpcms.plugins.wrapper.ContentWrapperHandler with information on layout
        @param url: action url in the form     
        '''
        instance = djp.instance
        request  = djp.request
        
        if isinstance(self.form,type):
            mform = modelform_factory(self.model, self.form)
        else:
            mform = self.form(request = request, instance = instance)
        
        initial = self.update_initial(request, mform, initial)
        
        wrapper  = djp.wrapper
                
        f     = mform(**form_kwargs(request     = request,
                                    initial     = initial,
                                    instance    = instance,
                                    prefix      = prefix,
                                    withrequest = self.form_withrequest))
        
        if wrapper:
            layout = wrapper.form_layout
        else:
            layout = None
        fl = formlet(form = f, layout = layout, submit = self.submit(instance))
        
        if wrapped:
            fhtml  = form(method = self.form_method, url = djp.url)
            if self.form_ajax:
                fhtml.addClass(self.ajax.ajax)
            fhtml['form'] = fl
            return fhtml
        else:
            return fl
        
    def submit(self, instance):
        if instance:
            sb = [submit(value = 'save', name = 'edit')]
        else:
            sb = [submit(value = 'add', name = 'add')]
        sb.append(submit(value = 'cancel', name = 'cancel'))
        return sb
    
    def get_searchform(self,
                       djp,
                       initial = None,
                       method  = 'get'):
        '''
        Build a search form for model
        '''
        mform  = self.search_form
        f = mform(**form_kwargs(request = djp.request,
                                initial = initial))
        fhtml = form(method = method, url = djp.url)
        fhtml['form'] = formlet(form = f,
                                layout = 'flat-notag',
                                submit = submit(value = 'search', name = 'search'))
        return fhtml
    
    def get_page(self):
        from djpcms.models import Page
        if self.haspage:
            pages = Page.object.get_for_model(self.model).filter(app_type = '')
            if not pages:
                raise valueError
            return page[0]
        else:
            return None
        
    def make_urls(self):
        '''
        Loop over children and create the django url view objects
        '''
        from django.conf.urls.defaults import patterns, url
        from djpcms.settings import CONTENT_INLINE_EDITING
        if self.editavailable:
            edit = CONTENT_INLINE_EDITING.get('preurl','edit')
        else:
            edit = None
            
        urls  = []
        # Loop over childre application to form the urls
        for child in self.applications.values():
            view_name  = self.get_view_name(child.name)
            nurl = url(regex = child.regex,
                       view  = child.response,
                       name  = view_name)
            urls.append(nurl)
            if edit and child.isapp:
                eview = editview(child,edit)
                self.edits.append(eview)
                nurl = url(regex = child.edit_regex(edit),
                           view  = eview.response,
                           name  = '%s_%s' % (edit,view_name))
                urls.append(nurl)
                
        return tuple(urls)
    urls = property(fget = make_urls)
    
    def addurl(self, request):
        view = self.getapp('add')
        if view and self.has_add_permission(request):
            djp = view.requestview(request)
            return djp.url
        
    def deleteurl(self, request, obj):
        #TODO: change this so that we are not tide up with name
        view = self.getapp('delete')
        if view and self.has_delete_permission(request, obj):
            djp = view.requestview(request, instance = obj)
            return djp.url
        
    def editurl(self, request, obj):
        '''
        Get the edit url if available
        '''
        #TODO: change this so that we are not tide up with name
        view = self.getapp('edit')
        if view and self.has_edit_permission(request, obj):
            djp = view.requestview(request, instance = obj)
            return djp.url
    
    def viewurl(self, request, obj):
        '''
        Get the view url if available
        '''
        #TODO: change this so that we are not tide up with name
        view = self.getapp('view')
        if view and self.has_view_permission(request, obj):
            djp = view.requestview(request, instance = obj)
            return djp.url
        
    def tagurl(self, request, tag):
        return None
    
    # Permissions
    #-----------------------------------------------------------------------------------------
    def has_permission(self, request = None, obj = None):
        return True
    def has_add_permission(self, request = None, obj=None):
        if not request:
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_add_permission())
    def has_edit_permission(self, request = None, obj=None):
        if not request:
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())
    def has_view_permission(self, request = None, obj=None):
        return self.has_permission(request, obj)
    def has_delete_permission(self, request = None, obj=None):
        if not request:
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission())
    #-----------------------------------------------------------------------------------------------
    
    def basequery(self, request):
        '''
        Starting queryset for searching objects in model.
        This can be re-implemented by subclasses.
        By default returns all
        '''
        return self.model.objects.all()
    
    def object_content(self, djp, obj):
        '''
        Utility function for getting content out of an instance of a model.
        This dictionary should be used to render an object within a template
        '''
        request = djp.request
        editurl = self.editurl(request, obj)
        if editurl:
            editurl = '%s?next=%s' % (editurl,djp.url)
        return {'item':      obj,
                'user':      request.user,
                'editurl':   editurl,
                'deleteurl': self.deleteurl(request, obj),
                'viewurl':   self.viewurl(request, obj)}
    
    def app_for_object(self, obj):
        try:
            if self.model == obj.__class__:
                return self
        except:
            pass
        return self.application_site.for_model(obj.__class__)
    
    def paginate(self, request, data, prefix, wrapper):
        '''
        paginate data
        @param request: HTTP request 
        @param data: a queryset 
        '''
        template_name = '%s/%s_search_item.html' % (self.opts.app_label,self.opts.module_name)
        pa = Paginator(data = data, request = request)
        for obj in pa.qs:
            content = self.object_content(djp, obj)
            yield loader.render_to_string(template_name, content)
    
    def render_object(self, djp):
        '''
        Render an object.
        This is usually called in the view page of the object
        '''
        obj      = djp.instance
        request  = djp.request
        template_name = self.get_object_view_template(obj,djp.wrapper)
        content = self.object_content(djp, obj)
        return loader.render_to_string(template_name    = template_name,
                                       context_instance = Context(content))
        
    def remove_object(self, obj):
        id = obj.id
        obj.delete()
        return id
        
    def data_generator(self, djp, data):
        '''
        Return a generator for the query.
        This function can be overritten by derived classes
        '''
        request = djp.request
        wrapper = djp.wrapper
        prefix  = djp.prefix
        app     = self
        for obj in data:
            content = app.object_content(djp, obj)
            yield loader.render_to_string(template_name    = self.get_item_template(obj, wrapper),
                                          context_instance = RequestContext(request, content))
    
    def get_object_view_template(self, obj, wrapper):
        '''
        Return the template file for the object
        The search looks in
         1 - components/<<module_name>>.html
         2 - <<app_label>>/<<module_name>>.html
         3 - djpcms/components/object.html (fall back)
        '''
        opts = obj._meta
        template_name = '%s.html' % opts.module_name
        return ['components/%s' % template_name,
                '%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object.html']
            
    def get_item_template(self, obj, wrapper):
        '''
        Search item template. Look in
         1 - components/<<module_name>>_search_item.html
         2 - <<app_label>>/<<module_name>>_search_item.html
         3 - djpcms/components/object_search_item.html (fall back)
        '''
        opts = obj._meta
        template_name = '%s_search_item.html' % opts.module_name
        return ['components/%s' % template_name,
                '%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object_search_item.html']
        
    def object_from_form(self, form):
        return form.save()
    
    def permissionDenied(self, djp):
        raise PermissionDenied


class ModelApplication(ModelApplicationBase):
    __metaclass__ = ModelAppMetaClass
    
