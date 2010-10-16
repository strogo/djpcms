'''
Application Model Manager
This module define the base class for implementing Dynamic Page views based on django models
The main object handle several subviews used for searching, adding and manipulating objects
'''
from copy import deepcopy

from django import http
from django.utils.encoding import force_unicode
from django.utils.datastructures import SortedDict
from django.template import loader, Template, Context, RequestContext
from django.conf.urls.defaults import url
from django import forms
from django.forms.models import modelform_factory

from djpcms.conf import settings
from djpcms.core.exceptions import PermissionDenied, ApplicationUrlException
from djpcms.utils import form_kwargs, UnicodeObject, slugify
from djpcms.utils.forms import add_hidden_field
from djpcms.plugins import register_application
from djpcms.utils.html import submit
from djpcms.utils.uniforms import UniForm
from djpcms.views.baseview import editview
from djpcms.views.appview import AppViewBase
from djpcms.views.cache import pagecache


class SearchForm(forms.Form):
    '''
    A simple search box
    '''
    search = forms.CharField(max_length=300, required = False,
                             widget = forms.TextInput(attrs={'class':'search-box'}))


def get_declared_application_views(bases, attrs):
    """Create a list of Application views instances from the passed in 'attrs', plus any
similar fields on the base classes (in 'bases')."""
    inherit = attrs.pop('inherit',False)
    apps = [(app_name, attrs.pop(app_name)) for app_name, obj in attrs.items() if isinstance(obj, AppViewBase)]      
    apps.sort(lambda x, y: cmp(x[1].creation_counter, y[1].creation_counter))

    # If this class is subclassing another Application, and inherit is True add that Application's views.
    # Note that we loop over the bases in *reverse*. This is necessary in
    # order to preserve the correct order of fields.
    if inherit:
        for base in bases[::-1]:
            if hasattr(base, 'base_views'):
                apps = base.base_views.items() + apps
                
    return SortedDict(data = apps)


class ApplicationMetaClass(forms.MediaDefiningClass):
    
    def __new__(cls, name, bases, attrs):
        attrs['base_views'] = get_declared_application_views(bases, attrs)
        new_class = super(ApplicationMetaClass, cls).__new__(cls, name, bases, attrs)
        return new_class


def process_views(view,views,app):
    pkey = view.parent
    if pkey:
        if isinstance(pkey,basestring):
            parent  = app.views.get(pkey,None)
            if not parent:
                raise ApplicationUrlException('Parent %s for %s not in children tree' % (pkey,view))
            view.parent = parent
        else:
            parent = pkey
        
        if parent in views:
            return process_views(parent,views,app)
        else:
            views.remove(view)
            return view
    else:
        if view is not app.root_application:
            view.parent = app.root_application
        views.remove(view)
        return view


class ApplicationBase(object):
    '''Base class for djpcms applications.
* *baseurl* the root part of the application views urls. Must be provided with trailing slashes (ex. "/docs/")
* *application_site* instance of the application site manager.
* *editavailable* ``True`` if inline editing is available.
    '''
    __metaclass__ = ApplicationMetaClass
    
    name             = None
    '''Application name. Default ``None``, calculated from class name.'''
    description      = None
    '''Application description. Default ``None``, calculated from name.'''
    authenticated    = True
    '''True if authentication is required. Default ``True``.'''
    has_api          = False
    '''Flag indicating if API is available. Default ``False``.'''
    inherit          = False
    '''Flag indicating if application views are inherited from base class. Default ``False``.'''
    hidden           = False
    '''If ``True`` the application is only used internally. Default ``False``.'''
    
    def __init__(self, baseurl, application_site, editavailable):
        self.application_site = application_site
        self.editavailable    = editavailable
        self.root_application = None
        if not baseurl.endswith('/'):
            baseurl = '%s/' % baseurl
        if not baseurl.startswith('/'):
            baseurl = '/%s' % baseurl
        self.__baseurl        = baseurl
        self.name             = self._makename()
        self.description      = self._makedescription()
        self.views            = deepcopy(self.base_views)
        self._create_views()
        urls = []
        for app in self.views.values():
            view_name  = self._get_view_name(app.name)
            nurl = url(regex = str(app.regex),
                       view  = app,
                       name  = view_name)
            urls.append(nurl)
        self.urls = tuple(urls)
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.baseurl)
    
    def __str__(self):
        return self.__repr__()
    
    def getview(self, code):
        '''Get an application view from the view code.'''
        return self.views.get(code, None)
    
    @property
    def ajax(self):
        return settings.HTML_CLASSES
        
    def get_root_code(self):
        raise NotImplementedError
    
    def __get_baseurl(self):
        return self.__baseurl
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
        '''Return True if the page can be viewed, otherwise False'''
        return True
    
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
            return app.parent(djp.request, **djp.kwargs)
    
    def _makename(self):
        cls = self.__class__
        name = cls.name
        if not name:
            name = cls.__name__
        name = name.replace('-','_').lower()
        return str(slugify(name,rtx='_'))
    
    def _makedescription(self):
        return self.description or self.name
    
    def _get_view_name(self, name):
        if not self.baseurl:
            raise ApplicationUrlException('Application without baseurl')
        base = self.baseurl[1:-1].replace('/','_')
        return '%s_%s' % (base,name)
    
    def _create_views(self):
        #Build views for this application
        roots = []
        
        # Find the root view
        for name,view in self.views.items():
            view.name = name
            view.code = u'%s-%s' % (self.name,view.name)
            if not view.parent:
                if not view.urlbit:
                    if self.root_application:
                        raise ApplicationUrlException('Could not resolve root application for %s' % self)
                    self.root_application = view
                else:
                    roots.append(view)
        
        # No root application. See if there is one candidate
        if not self.root_application:
            if roots:
                #just pick one. We should not be here really! need more testing.
                self.root_application = roots[0]
            else:
                raise ApplicationUrlException("Could not define root application for %s." % self)
        
        # Pre-process urls
        views = self.views.values()
        while views:
            view = process_views(views[0],views,self)
            view.processurlbits(self)
            if view.isapp:
                name = u'%s %s' % (self.name,view.name.replace('_',' '))
                self.application_site.choices.append((view.code,name))
            if view.isplugin:
                register_application(view)
                


class ModelApplication(ApplicationBase):
    '''
    Base class for Django Model Applications
    This class implements the basic functionality for a general model
    User should subclass this for full control on the model application.
    Each one of the class attributes are optionals.
    '''    
    '''Form method'''
    list_display     = None
    '''List of object's field to display. If available, the search view will display a sortable table
of objects. Default is ``None``.'''
    list_per_page    = 30
    '''Number of objects per page. Default is ``30``.'''
    filter_fields    = None
    '''List of model fields which can be used to filter'''
    form             = forms.ModelForm
    '''Form class to edit/add objects of the application model.'''
    form_method      ='post'
    '''Form submit method, ``get`` or ``post``. Default ``post``.'''
    form_withrequest = False
    '''If set to True, the request instance is passed to the form constructor. Default is ``False``.'''
    form_ajax        = True
    '''If True the form submits are performed using ajax. Default ``True``.'''
    form_template    = None
    '''Optional template for form. Can be a callable with parameter ``djp``. Default ``None``.'''
    in_navigation    = True
    '''True if application'views can go into site navigation. Default ``True``.'''
    search_fields    = None
    '''List of model field's names which are searchable. Default ``None``.'''
    
    _form_add        = 'add'
    _form_edit       = 'change'
    _form_save       = 'done'
    _form_continue   = 'save & continue'
    #
    search_form      = SearchForm
    # If set to True, base class views will be available
    #
    #
    list_display_links = None
    
    def __init__(self, baseurl, application_site, editavailable, model = None):
        self.model            = model
        self.opts             = model._meta
        super(ModelApplication,self).__init__(baseurl, application_site, editavailable)
        #self.edits            = []
        
    def get_root_code(self):
        return self.root_application.code
    
    def modelsearch(self):
        return self.model
    
    def get_search_fields(self):
        if self.search_fields:
            return self.search_fields
        else:
            from django.contrib.admin import site
            admin = site._registry.get(self.modelsearch(),None)
            if admin:
                return admin.search_fields
        
    def objectbits(self, obj):
        '''Get arguments from model instance used to construct url. By default it is the object id.
* *obj*: instance of self.model

It returns dictionary of url bits. 
        '''
        return {'id': obj.id}
    
    def get_object(self, *args, **kwargs):
        '''Retrive an instance of self.model from key-values *kwargs* forming the url.
By default it get the 'id' and get the object::

    try:
        id = int(kwargs.get('id',None))
        return self.model.objects.get(id = id)
    except:
        return None
    
Reimplement for custom arguments.'''
        try:
            id = int(kwargs.get('id',None))
            return self.model.objects.get(id = id)
        except:
            return None
    
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
    def get_form(self,
                 djp,
                 initial = None,
                 prefix = None,
                 wrapped = True,
                 form = None,
                 addinputs = True,
                 withdata = True,
                 forceform = False):
        '''Build a form to add or edit an application model object:
        
 * *djp*: instance of djpcms.views.DjpRequestWrap.
 * *initial*: If not none, a dictionary of initial values for model fields.
 * *prefix*: prefix to use in the form.
 * *wrapper*: instance of djpcms.plugins.wrapper.ContentWrapperHandler with information on layout.
'''
        instance = djp.instance
        request  = djp.request
        own_view = djp.own_view()
        
        form = form or self.form
        
        if isinstance(form,type):
            if forceform:
                mform = form
            else:
                try:
                    if form._meta.model == self.model:
                        mform = form
                except:
                    mform = modelform_factory(self.model, form)
                else:
                    mform = modelform_factory(self.model, form)
        else:
            mform = form(request = request, instance = instance)
        
        initial = self.update_initial(request, mform, initial, own_view = own_view)
        
        wrapper  = djp.wrapper
                
        f     = mform(**form_kwargs(request     = request,
                                    initial     = initial,
                                    instance    = instance,
                                    prefix      = prefix,
                                    withdata    = withdata,
                                    withrequest = self.form_withrequest))
        inputs = None
        if addinputs:
            inputs = self.submit(instance, own_view)
        
        template = self.form_template
        if callable(template):
            template = template(djp)
            
        wrap = UniForm(f,
                       request  = request,
                       instance = instance,
                       action   = djp.url,
                       inputs   = inputs,
                       template = template)
        if self.form_ajax:
            wrap.addClass(self.ajax.ajax)
        wrap.is_ajax = request.is_ajax()
        wrap.addClass(str(self.model._meta).replace('.','-'))
        return wrap
        
    def submit(self, instance, own_view = False):
        '''Generate the submits elements to be added to the model form.
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
    
    def object_from_form(self, form):
        '''Save form and return an instance pof self.model'''
        return form.save()
    
    # APPLICATION URLS
    #----------------------------------------------------------------
    def appviewurl(self, request, name, obj = None, permissionfun = None, objrequired=False):
        if objrequired and not isinstance(obj,self.model):
            return None
        try:
            view = self.getview(name)
            permissionfun = permissionfun or self.has_view_permission
            if view and permissionfun(request, obj):
                djp = view(request, instance = obj)
                return djp.url
        except:
            return None
        
    def addurl(self, request):
        return self.appviewurl(request,'add',None,self.has_add_permission)
        
    def deleteurl(self, request, obj):
        return self.appviewurl(request,'delete',obj,self.has_delete_permission,objrequired=True)
        
    def editurl(self, request, obj):
        return self.appviewurl(request,'edit',obj,self.has_edit_permission,objrequired=True)
    
    def viewurl(self, request, obj):
        return self.appviewurl(request,'view',obj,objrequired=True)
    
    def searchurl(self, request):
        return self.appviewurl(request,'search')
        
    def objurl(self, request, name, obj = None):
        '''Application view **name** url.'''
        view = self.getview(name)
        if not view:
            return None
        permission_function = getattr(self,
                                      'has_%s_permission' % name,
                                      self.has_permission)
        try:
            if permission_function(request,obj):
                djp = view(request, instance = obj)
                return djp.url
            else:
                return None
        except:
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
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)
    
    def has_view_permission(self, request = None, obj = None):
        '''Return True if the page can be viewed, otherwise False'''
        if not request:
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.view', obj)
    
    def has_delete_permission(self, request = None, obj=None):
        if not request:
            return False
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)
    #-----------------------------------------------------------------------------------------------
    
    def basequery(self, request):
        '''
        Starting queryset for searching objects in model.
        This can be re-implemented by subclasses.
        By default returns all
        '''
        return self.model.objects.all()
    
    def object_content(self, djp, obj):
        '''Utility function for getting content out of an instance of a model.
This dictionary should be used to render an object within a template. It returns a dictionary.'''
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
        '''Paginate data
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
        '''Return the template file which render the object *obj*.
        The search looks in
         1 - components/<<model_name>>.html
         2 - <<app_label>>/<<model_name>>.html
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
    
    def permissionDenied(self, djp):
        raise PermissionDenied
        
    def sitemapchildren(self, view):
        return []
    
    def instancecode(self, request, obj):
        '''Obtain an unique code for an instance.
Can be overritten to include request dictionary.'''
        return '%s:%s' % (obj._meta,obj.id)
    
    