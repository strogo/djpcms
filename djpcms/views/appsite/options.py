'''
Application Model Manager
This module define the base class for implementing Dynamic Page views based on django models
The main object handle several subviews used for searching, adding and manipulating objects
'''
from copy import deepcopy

from django import forms, http
from django.forms.models import modelform_factory
from django.utils.encoding import force_unicode
from django.utils.datastructures import SortedDict
from django.template import loader, Template, Context, RequestContext
from django.core.exceptions import PermissionDenied
from django.conf.urls.defaults import url


from djpcms.conf import settings
from djpcms.utils import form_kwargs, UnicodeObject
from djpcms.utils.forms import add_hidden_field
from djpcms.plugins import register_application
from djpcms.utils.html import formlet, submit, form, FormHelper

from djpcms.views.baseview import editview
from djpcms.views.appview import AppView
from djpcms.views.cache import pagecache


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
                
    return SortedDict(data = apps)


class ApplicationBase(object):
    '''
    Base class for djpcms applications
    '''
    ajax             = settings.HTML_CLASSES
    name             = None
    authenticated    = True
    has_api          = False
    
    def __init__(self, baseurl, application_site, editavailable):
        self.application_site = application_site
        self.editavailable    = editavailable
        self.root_application = None
        self.__baseurl = baseurl
        
    def get_root_code(self):
        raise NotImplementedError
    
    def __get_baseurl(self):
        return self.__baseurl
    #    page = pagecache.get_for_application(self.get_root_code())
    #    if page:
    #        return page.url
    #    else:
    #        return None
    baseurl = property(__get_baseurl)
    
    def __call__(self, request, rurl):
        from django.core import urlresolvers
        resolver = urlresolvers.RegexURLResolver(r'^', self.urls)
        return resolver.resolve(rurl)
    
    def isroot(self):
        return True
    
    def get_the_view(self):
        return self.root_application
    
    def has_permission(self, request = None, obj = None):
        return True



class ModelApplicationBase(ApplicationBase):
    '''
    Base class for Django Model Applications
    This class implements the basic functionality for a general model
    User should subclass this for full control on the model application.
    Each one of the class attributes are optionals
    '''
    # Form used for adding/editing objects.
    form             = forms.ModelForm
    _form_add        = 'add'
    _form_edit       = 'change'
    _form_save       = 'done'
    _form_continue   = 'save & continue'
    # Form layout.
    form_layout      = None
    # Whether the form requires the request object to be passed to the constructor
    form_withrequest = False
    # Form response method, POST by default
    form_method      ='post'
    # if True add/edit/delete will be performed via AJAX xhr POST requests
    form_ajax        = True
    search_form      = None
    #
    date_code        = None
    search_form      = SearchForm
    # True if applications can go into navigation
    in_navigation    = True
    # If set to True, base class views will be available
    inherit          = False
    #
    search_fields    = None
    #
    list_display     = None
    #
    list_display_links = None
    
    def __init__(self, baseurl, application_site, editavailable, model = None):
        super(ModelApplicationBase,self).__init__(baseurl, application_site, editavailable)
        self.model            = model
        self.opts             = model._meta
        self.name             = self.name or self.opts.module_name
        self.applications     = deepcopy(self.base_applications)
        self.edits            = []
        self.parent_url       = None
        self.create_applications()
        urls = []
        for app in self.applications.values():
            view_name  = self.get_view_name(app.name)
            nurl = url(regex = str(app.regex),
                       view  = app,
                       name  = view_name)
            urls.append(nurl)
        self.urls = tuple(urls)
        
    def get_root_code(self):
        return self.root_application.code
        
    def create_applications(self):
        '''
        Build sub views for this application
        '''
        roots = []
        for app_name,child in self.applications.items():
            child.name   = app_name
            pkey         = child.parent
            if pkey:
                parent  = self.applications.get(pkey,None)
                if not parent:
                    raise ModelApplicationUrlError('Parent %s for %s not in children tree' % (pkey,child))
                child.parent = parent
            else:
                if not child.urlbit:
                    if self.root_application:
                        raise ValueError('Could not resolve root application')
                    self.root_application = child
                else:
                    roots.append(child)
            child.processurlbits(self)
            code = u'%s-%s' % (self.name,child.name)
            child.code = code
            #
            # View with no arguments. Store in parent pages
            #TODO: This is useless, remove it!
            #if not child.tot_args:
            #    self.application_site.root_pages[child.purl] = child
                
            if child.isapp:
                name = u'%s %s' % (self.name,child.name.replace('_',' '))
                self.application_site.choices.append((code,name))
            if child.isplugin:
                register_application(child)
        #
        # Check for parents
        if roots and self.root_application:
            for app in roots:
                app.parent = self.root_application
                                
    def get_search_fields(self):
        if self.search_fields:
            return self.search_fields
        else:
            from django.contrib.admin import site
            admin = site._registry.get(self.model,None)
            if admin:
                return admin.search_fields
        
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
    
    def getapp(self, code):
        return self.applications.get(code, None)
    
    def update_initial(self, request, mform, initial = None, own_view = True):
        if request.method == 'GET':
            params = dict(request.GET.items())
            next   = params.get('next',None)
            if not next and not own_view:
                next = request.path
            if next:
                mform = add_hidden_field(mform,'next')
                initial = initial or {}
                initial['next'] = next
        return initial
    
    def get_extra_forms(self):
        return None
    
    #  FORMS FOR EDITING AND SEARCHING
    #---------------------------------------------------------------------------------
    def get_form(self, djp, prefix = None, initial = None, wrapped = True, formhelper = True, form = None):
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
        own_view = djp.url == request.path
        
        form = form or self.form
        
        if isinstance(form,type):
            mform = modelform_factory(self.model, form)
        else:
            mform = form(request = request, instance = instance)
        
        initial = self.update_initial(request, mform, initial, own_view = own_view)
        
        wrapper  = djp.wrapper
                
        f     = mform(**form_kwargs(request     = request,
                                    initial     = initial,
                                    instance    = instance,
                                    prefix      = prefix,
                                    withrequest = self.form_withrequest))

        if formhelper:
            helper = getattr(f,'helper',None)
            if not helper:
                helper = FormHelper()
                f.helper = helper
            
            helper.attr['action'] = djp.url
            if helper.ajax is not False and self.form_ajax:
                helper.addClass(self.ajax.ajax)
            helper.inputs = self.submit(instance, own_view)
            return f
        
        
        layout = self.form_layout
        if not layout and wrapper:
            layout = wrapper.form_layout
            
        submit = self.submit(instance, own_view)
        fl = formlet(form = f, layout = layout, submit = submit)
        
        if wrapped:
            fhtml  = form(method = self.form_method, url = djp.url)
            if self.form_ajax:
                fhtml.addClass(self.ajax.ajax)
            fhtml['form'] = fl
            return fhtml
        else:
            return fl
        
    def submit(self, instance, own_view):
        '''
        Submits elements
        '''
        if instance:
            sb = [submit(value = self._form_save, name = '_save')]
        else:
            sb = [submit(value = self._form_add, name = '_save')]
        if self._form_continue and own_view:
            sb.append(submit(value = self._form_continue, name = '_save_and_continue'))
        if own_view:
            sb.append(submit(value = 'cancel', name = '_cancel'))
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
    
    # APPLICATION URLS
    # TODO: write it better (not use of application name)
    #----------------------------------------------------------------
    def addurl(self, request):
        view = self.getapp('add')
        if view and self.has_add_permission(request):
            djp = view(request)
            return djp.url
        
    def deleteurl(self, request, obj):
        #TODO: change this so that we are not tide up with name
        view = self.getapp('delete')
        if view and self.has_delete_permission(request, obj):
            djp = view(request, instance = obj)
            return djp.url
        
    def editurl(self, request, obj):
        '''
        Get the edit url if available
        '''
        #TODO: change this so that we are not tide up with name
        view = self.getapp('edit')
        if view and self.has_edit_permission(request, obj):
            djp = view(request, instance = obj)
            return djp.url
    
    def viewurl(self, request, obj):
        '''
        Get the view url if available
        '''
        #TODO: change this so that we are not tide up with name
        try:
            view = self.getapp('view')
            if view and self.has_view_permission(request, obj):
                djp = view(request, instance = obj)
                return djp.url
        except:
            return None
    
    def searchurl(self, request):
        '''
        The search url for the model
        '''
        view = self.getapp('search')
        if view and self.has_view_permission(request):
            djp = view(request)
            return djp.url
        
    def tagurl(self, request, tag):
        return None
    
    # PERMISSIONS
    #-----------------------------------------------------------------------------------------
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
                'djp':       djp,
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
    
    def render_object(self, djp, wrapper = None):
        '''
        Render an object.
        This is usually called in the view page of the object
        '''
        obj      = djp.instance
        request  = djp.request
        template_name = self.get_object_view_template(obj, wrapper or djp.wrapper)
        content = self.object_content(djp, obj)
        return loader.render_to_string(template_name    = template_name,
                                       context_instance = Context(content))
        
    def title_object(self, obj):
        '''
        Return the title of a object-based view
        '''
        return '%s' % obj
        
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
        template_name = '%s_list_item.html' % opts.module_name
        return ['components/%s' % template_name,
                '%s/%s' % (opts.app_label,template_name),
                'djpcms/components/object_list_item.html']
        
    def object_from_form(self, form):
        return form.save()
    
    def permissionDenied(self, djp):
        raise PermissionDenied
    
    def parentresponse(self, djp, app):
        '''
        Retrive the parent view
        '''
        if not app.parent:
            page = app.get_page()
            if page:
                page = page.parent
                if page:
                    app.parent = pagecache.view_from_page(djp.request, page)
        if app.parent:
            return app.parent(djp.request, **djp.urlargs)
        
    def sitemapchildren(self, view):
        return []


class ModelAppMetaClass(forms.MediaDefiningClass):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_applications'] = get_declared_applications(bases, attrs)
        new_class = super(ModelAppMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class
    


class ModelApplication(ModelApplicationBase):
    __metaclass__ = ModelAppMetaClass
    

