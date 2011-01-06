import operator
from copy import copy
from datetime import datetime

# Hack for Python 2.6 -> Python 3
try:
    from itertools import izip as zip
except ImportError:
    import zip

from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import smart_split

from djpcms.utils.translation import ugettext as _
from djpcms.template import loader, RequestContext
from djpcms.forms import saveform, deleteinstance, autocomplete
from djpcms.utils.html import Paginator
from djpcms.utils import construct_search, isexact
from djpcms.views.regex import RegExUrl
from djpcms.views.baseview import djpcmsview


class pageinfo(object):
    
    def __init__(self,url,last_modified):
        self.url = url
        self.last_modified = last_modified


def selfmethod(self, f):
    def _(*args, **kwargs):
        return f(self, *args, **kwargs)
    _.__name__ = f.__name__
    return _


class View(djpcmsview):
    '''This is a specialised view class derived from :class:`djpcms.views.baseview.djpcmsview`
and used for handling views which belongs to
:ref:`djpcms applications <topics-applications-index>`.

They are specified as class attributes of
:class:`djpcms.views.appsite.ApplicationBase` and therefore initialised
at start up.

Views which derives from class are special in the sense that they can also
appear as content of :class:`djpcms.plugins.DJPplugin` if
the :attr:`isplugin` is set to ``True``.

All parameters are optionals and usually a small subset of them needs to be used.

:keyword parent: Parent application name. If not supplied, ``djpcms`` will calculate it
                 during validation of applications at startup. It is used to
                 assign a value to the :attr:`parent` attribute. Default ``None``.
:keyword regex: Regular expression for view-specific url.
                This is the url which the view add to its parent url. Default ``None``.
:keyword isapp: If ``True`` the view will be treated as an application view and therefore added to the list
                of applications which can be associated with a :class:`djpcms.models.Page` object.
                Its value is assigned to the :attr:`isapp` attribute. Default ``False``.
:keyword isplugin: If ``True`` the view can be rendered as :class:`djpcms.plugins.ApplicationPlugin`.
                  Its value is assigned to the :attr:`isplugin` attribute. Default ``False``.
:keyword form: Form class or ``None``. If supplied it will be assigned to the :attr:`_form` attribute.
               It is a form which can be used for interaction. Default ``None``.
:keyword methods: Tuple used to specify the response method allowed ('get', 'post', put') ro ``None``.
                  If specified it replaces the :attr:`_methods` attribute.
                  Default ``None``.
:keyword view_template: Template file used to render the view. Default ``None``.
                        If specified it replaces the :attr:`view_template` attribute.
:keyword renderer: A one parameters functions which can be used to replace the
                   default :meth:`render` method. Default ``None``. The function
                   must return a safe string ready for rendering on a HTML page.
:keyword permission: A three parameters function which can be used to
                     replace the default :meth:`_has_permission` method.
                     Default ``None``. The function
                     return a boolean and takes the form::
                     
                         def permission(view, request, obj):
                             ...
                         
                     where ``self`` is an instance of the view, ``request`` is the HTTP request instance and
                     ``obj`` is an instance of model or ``None``.
:keyword headers: List of string to display as table header when the
                  view display a table. Default ``None``.
Usage::

    from djpcms.views import appview, appsite
    
    class MyApplication(appsite.ApplicationBase):
        home = appview.View(renderer = lambda s, djp : 'Hello world')
        test = appview.View(regex = 'testview', renderer = lambda s, djp : 'Another view')
    
.. attribute:: parent

    instance of :class:`View` or None.
    
.. attribute:: _form

    Form class associated with view. Default ``None``.
    
.. attribute:: isapp

    if ``True`` the view will be added to the application list and can have its own page object. Default ``False``.
    
.. attribute:: isplugin

    if ``True`` the view can be rendered as :class:`djpcms.plugins.ApplicationPlugin`. Default ``False``.

.. attribute:: in_navigation

    If ``0`` the view won't appear in :ref:`Navigation <topics-included-navigator>`.
    
.. attribute:: view_template

    Template file or list of template files used to render
    the view (not the whole page). Default ``djpcms/components/pagination.html``.
    
.. attribute:: plugin_form

    The :attr:`djpcms.plugins.DJPplugin.form` for this view. Default ``None``.
'''
    creation_counter = 0
    plugin_form    = None
    view_template  = 'djpcms/components/pagination.html'
    force_redirect = False
    _form          = None
    _form_ajax     = None
    
    def __init__(self,
                 parent        = None,
                 regex         = None,
                 splitregex    = False,
                 insitemap     = True,
                 isapp         = False,
                 isplugin      = False,
                 methods       = None,
                 plugin_form   = None,
                 renderer      = None,
                 permission    = None,
                 in_navigation = 0,
                 template_name = None,
                 view_template = None,
                 description    = None,
                 force_redirect = None,
                 form           = None,
                 form_withrequest = None,
                 form_ajax     = None,
                 headers       = None,
                 astable        = False,
                 table_generator = None,
                 success_message = None):
        self.name        = None
        self.description = description
        self.parent    = parent
        self.isapp     = isapp
        self.isplugin  = isplugin
        self.in_nav    = in_navigation
        self.appmodel  = None
        self.insitemap = insitemap
        self.urlbit    = RegExUrl(regex,splitregex)
        self.regex     = None
        self.func      = None
        self.code      = None
        self.editurl   = None
        self.headers   = headers
        self.astable   = astable
        if table_generator:
            self.table_generator = table_generator
        if renderer:
            self.render = renderer
        if permission:
            self._has_permission = permission
        if methods:
            self._methods = methods
        if template_name:
            self.template_name = template_name
        if success_message:
            self.success_message = success_message
        if view_template:
            self.view_template = view_template
        if force_redirect is not None:
            self.force_redirect = force_redirect
        self._form     = form if form else self._form
        self._form_withrequest = form_withrequest
        self._form_ajax  = form_ajax if form_ajax is not None else self._form_ajax
        self.plugin_form = plugin_form or self.plugin_form
        self.creation_counter = View.creation_counter
        View.creation_counter += 1
        
    def __get_baseurl(self):
        return self.appmodel.baseurl
    baseurl = property(__get_baseurl)
    
    def get_url(self, djp, **kwargs):
        purl = self.regex.get_url(**kwargs)
        return '%s%s' % (self.baseurl,purl)
    
    def names(self):
        return self.regex.names
    
    def get_media(self):
        return self.appmodel.media
    
    def in_navigation(self, request, page):
        if page:
            if self.regex.names and not page.url_pattern:
                return 0
            else:
                return page.in_navigation
        if self.in_nav:
            return 1
        else:
            return 0
        
    def linkname(self, djp):
        page = djp.page
        link = '' if not page else page.link
        if not link:
            link = self.appmodel.name
        return link
        
    def title(self, page, **kwargs):
        title = None if not page else page.title
        return title or self.appmodel.name
    
    def isroot(self):
        '''True if this application view represents the root view of the application.'''
        return self.appmodel.root_application is self
    
    def get_form(self, djp,
                 form = None,
                 form_withrequest = None,
                 form_ajax = None,
                 **kwargs):
        form_withrequest = form_withrequest if form_withrequest is not None else self._form_withrequest
        form_ajax = form_ajax if form_ajax is not None else self._form_ajax
        return self.appmodel.get_form(djp,
                                      form or self._form,
                                      form_withrequest = form_withrequest,
                                      form_ajax = form_ajax,
                                      **kwargs)
        
    def is_soft(self, djp):
        page = djp.page
        return False if not page else page.soft_root
        
    def get_page(self, djp):
        pages = djp.pagecache.get_for_application(self.code)
        if pages:
            if len(pages) == 1:
                return pages[0]
            else:
                request = djp.request
                kwargs = djp.kwargs.copy()
                kwargs.pop('instance',None)
                page   = pages.filter(url_pattern = '')
                if page:
                    page = page[0]
                    try:
                        url  = self.get_url(djp, **kwargs)
                        for p in pages:
                            if p.url == url:
                                page = p
                                break
                    except:
                        pass
                    return page
        if self.parent:
            return self.parent.get_page(djp)
        
    def specialkwargs(self, page, kwargs):
        if page:
            names = self.regex.names
            if names:
                kwargs = kwargs.copy()
                if page.url_pattern:
                    bits = page.url_pattern.split('/')
                    kwargs.update(dict(zip(self.regex.names,bits)))
                else:
                    for name in names:
                        kwargs.pop(name,None)
        return kwargs
    
    def has_permission(self, request = None, page = None, obj = None):
        if super(View,self).has_permission(request, page, obj):
            return self._has_permission(request, obj)
        else:
            return False
        
    def _has_permission(self, request, obj):
        return self.appmodel.has_permission(request, obj)
    
    def render(self, djp):
        '''Render the view. This method is reimplemented by subclasses or
replaced during initialization.

:keyword djp: instance of :class:`djpcms.views.response.DjpResponse`.'''
        pass
    
    def render_query(self, djp, query, appmodel = None):
        '''Render a queryset'''
        appmodel = appmodel or self.appmodel
        p  = Paginator(djp.request, query, per_page = appmodel.list_per_page)
        c  = copy(djp.kwargs)
        headers = self.headers or appmodel.list_display
        if callable(headers):
            headers = headers(djp)
        astable = headers and self.astable
        c.update({'paginator': p,
                  'astable': astable,
                  'djp': djp,
                  'url': djp.url,
                  'model': appmodel.model,
                  'css': djp.css,
                  'appmodel': appmodel,
                  'headers': headers})
        
        if astable:
            c['items'] = self.table_generator(djp, p.qs)
        else:    
            c['items'] = self.data_generator(djp, p.qs)
            
        return loader.render_to_string(self.view_template, c)
    
    def parentresponse(self, djp):
        '''
        Retrive the parent response
        '''
        return self.appmodel.parentresponse(djp, self)
    
    def table_generator(self, djp, qs):
        return self.appmodel.table_generator(djp, qs)
    
    def data_generator(self, djp, qs):
        return self.appmodel.data_generator(djp, qs)
    
    def processurlbits(self, appmodel):
        '''Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        self.css      = appmodel.ajax
        if self.parent:
            self.regex = self.parent.regex + self.urlbit
        else:
            self.regex = self.urlbit
            
    def __deepcopy__(self, memo):
        return copy(self)  
    
    
class ModelView(View):
    '''A :class:`View` class for views in :class:`djpcms.views.appsite.ModelApplication`.
    '''
    def __init__(self, isapp = True, splitregex = True, **kwargs):
        super(ModelView,self).__init__(isapp = isapp,
                                       splitregex = splitregex,
                                       **kwargs)
        
    def __unicode__(self):
        return u'%s: %s' % (self.name,self.regex)
    
    def __get_model(self):
        return self.appmodel.model
    model = property(fget = __get_model)
    
    def edit_regex(self, edit):
        baseurl = self.baseurl
        if baseurl:
            return r'^%s/%s%s$' % (edit,baseurl[1:],self.regex)
        else:
            return None
    
    def modelparent(self):
        '''
        Return a parent with same model if it exists
        '''
        p = self.parent
        if p:
            if getattr(p,'model',None) == self.model:
                return p
        return None
    
    def appquery(self, djp):
        '''This function implements the query to the database, based on url entries.
By default it calls the :func:`djpcms.views.appsite.ModelApplication.basequery` function.'''
        return self.appmodel.basequery(djp)
    
    def permissionDenied(self, djp):
        return self.appmodel.permissionDenied(djp)
    
    def sitemapchildren(self):
        return []
    
    def defaultredirect(self, request, **kwargs):
        return model_defaultredirect(self, request, **kwargs)
    
    
def model_defaultredirect(self, request, next = None, instance = None, **kwargs):
    if instance:
        next = self.appmodel.viewurl(request,instance)
    if not next:
        next = self.appmodel.baseurl
    return super(ModelView,self).defaultredirect(request, next = next,
                                                 instance = instance, **kwargs)
    
    
class SearchView(ModelView):
    '''A :class:`ModelView` class for searching objects in model.
By default :attr:`View.in_navigation` is set to ``True``.
There are three additional parameters that can be set:

:keyword astable: used to force the view not as a table. Default ``True``.
:keyword table_generator: Optional function to generate table content. Default ``None``.
:keyword search_text: string identifier for text queries.
    '''
    search_text = 'q'
    '''identifier for queries. Default ``q``.'''
    
    def __init__(self, in_navigation = True, astable = True, search_text = None, **kwargs):
        self.search_text = search_text or self.search_text
        super(SearchView,self).__init__(in_navigation=in_navigation,
                                        astable=astable,
                                        **kwargs)
    
    def appquery(self, djp):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        qs = super(SearchView,self).appquery(djp)
        request = djp.request
        slist = self.appmodel.opts.search_fields
        if request.method == 'GET':
            data = dict(request.GET.items())
        else:
            data = dict(request.POST.items())
        search_string = data.get(self.search_text,None)
        if slist and search_string:
            bits  = smart_split(search_string)
            #bits  = search_string.split(' ')
            for bit in bits:
                bit = isexact(bit)
                if not bit:
                    continue
                or_queries = [Q(**{construct_search(field_name): bit}) for field_name in slist]
                other_qs   = QuerySet(self.appmodel.modelsearch())
                other_qs.dup_select_related(qs)
                other_qs   = other_qs.filter(reduce(operator.or_, or_queries))
                qs         = qs & other_qs    
        return qs
    
    def render(self, djp):
        '''Perform the custom query over the model objects and return a paginated result
        '''
        query = self.appquery(djp)
        return self.render_query(djp, query)  


class AddView(ModelView):
    '''A :class:`ModelView` class which renders a form for adding instances
and handles the saving as default ``POST`` response.'''
    def __init__(self, regex = 'add', isplugin = True,
                 in_navigation = True, **kwargs):
        super(AddView,self).__init__(regex  = regex,
                                     isplugin = isplugin,
                                     in_navigation = in_navigation,
                                     **kwargs)
    
    def _has_permission(self, request, obj):
        return self.appmodel.has_add_permission(request, obj)
    
    def save(self, request, f):
        return self.appmodel.object_from_form(f)
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def default_post(self, djp):
        return saveform(djp, False, force_redirect = self.force_redirect)
    
    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)

            
class ObjectView(ModelView):
    '''A :class:`ModelView` class view for model instances.
A view of this type has an embedded object available which is used to generate the full url.'''
    object_view = True
    
    def get_url(self, djp, instance = None, **kwargs):
        if instance:
            kwargs.update(self.appmodel.objectbits(instance))
        else:
            instance = self.appmodel.get_object(djp.request, **kwargs)
        
        if not instance:
            raise djp.http.Http404
        
        if djp:
            djp.instance = instance
        return super(ObjectView,self).get_url(djp, **kwargs)
    
    def title(self, page, instance = None, **kwargs):
        return self.appmodel.title_object(instance)

    def defaultredirect(self, request, next = None, instance = None, **kwargs):
        return model_defaultredirect(self, request, next = next,
                                     instance = instance, **kwargs)
    

class ViewView(ObjectView):
    '''An :class:`ObjectView` class specialised for displaying an object.
    '''
    def __init__(self, regex = '(?P<id>\d+)', **kwargs):
        super(ViewView,self).__init__(regex = regex, **kwargs)
    
    def linkname(self, djp):
        return str(djp.instance)
        
    def render(self, djp):
        '''Render the view object
        '''
        return self.appmodel.render_object(djp)
    
    def sitemapchildren(self):
        return self.appmodel.sitemapchildren(self)    
    
    
# Delete an object. POST method only. not GET method should modify databse
class DeleteView(ObjectView):
    '''An :class:`ObjectView` class specialised for deleting an object.
    '''
    _methods      = ('post',)
    
    def __init__(self, regex = 'delete', parent = 'view', isapp = False, **kwargs):
        super(DeleteView,self).__init__(regex = regex,
                                        parent = parent,
                                        isapp = isapp,
                                        **kwargs)
        
    def _has_permission(self, request, obj):
        return self.appmodel.has_delete_permission(request, obj)
    
    def remove_object(self, instance):
        return self.appmodel.remove_object(instance)
    
    def default_post(self, djp):
        return deleteinstance(djp, force_redirect = self.force_redirect)
    
    def nextviewurl(self, djp):
        view = djp.view
        if view.object_view and getattr(view,'model',None) == self.model:
            return self.appmodel.root_application(djp).url
        else: 
            return djp.url
      

# Edit/Change an object
class EditView(ObjectView):
    '''An :class:`ObjectView` class specialised for editing an object.
    '''
    def __init__(self, regex = 'edit', parent = 'view', **kwargs):
        super(EditView,self).__init__(regex = regex, parent = parent, **kwargs)
    
    def _has_permission(self, request, obj):
        return self.appmodel.has_edit_permission(request, obj)
    
    def title(self, page, instance = None, **kwargs):
        return 'Edit %s' % self.appmodel.title_object(instance)
    
    def render(self, djp):
        return self.get_form(djp).render(djp)
    
    def save(self, request, f):
        as_new = request.POST.has_key("_save_as_new")
        return self.appmodel.object_from_form(f)
    
    def default_post(self, djp):
        return saveform(djp, True, force_redirect = self.force_redirect)
    
    
class AutocompleteView(SearchView):
    '''This is an interesting view. It is an **AJAX Get only** view for :ref:`auto-complete <autocomplete>` functionalities.
To use it, add it to a :class:`djpcms.views.appsite.ModelApplication` declaration.

Let's say you have a model::

    from django.db import models
    
    class MyModel(models.Model):
        name = models.CharField(max_length = 60)
        description = models.TextField()
    
And we would like to have an auto-complete view which displays the ``name`` field and search for both
``name`` and ``description`` fields::

    from djpcms.views.appsite import ModelApplication
    
    class MyModelApp(ModelApplication):
        search_fields = ['name','description']
        complete = AutocompleteView(display = 'name')
        
    appsite.site.register('/mymodelurl/', MyModelApp, model = MyModel)
    
The last bit of information is to use a different ``ModelChoiceField`` and ``ModelMultipleChoiceField`` in
your forms. Rather than doing::

    from django.forms import ModelChoiceField, ModelMultipleChoiceField
    
do::
    
    from djpcms.forms import ModelChoiceField, ModelMultipleChoiceField
    
and if your model has an AutocompleteView installed, it will work out of the box.
'''
    _methods = ('get',)
    
    def __init__(self, regex = 'autocomplete', display = 'name', **kwargs):
        self.display = display
        super(AutocompleteView,self).__init__(regex = regex, **kwargs)
        
    def processurlbits(self, appmodel):
        super(AutocompleteView,self).processurlbits(appmodel)
        autocomplete.register(self.appmodel.model,self)
    
    def get_url(self, *args, **kwargs):
        purl = self.regex.get_url()
        return '%s%s' % (self.baseurl,purl)
        
    def get_response(self, djp):
        '''This response works only if it is an AJAX response. Otherwise it raises a ``Http404`` exception.'''
        request = djp.request
        if not request.is_ajax():
            raise djp.http.Http404
        params = dict(request.GET.items())
        query = request.GET.get('q', None)
        search_fields = self.appmodel.search_fields
        if query and search_fields:
            q = None
            for field_name in search_fields:
                name = construct_search(field_name)
                if q:
                    q = q | Q( **{str(name):query} )
                else:
                    rel_name = name.split('__')[0]
                    q = Q( **{str(name):query} )
            qs = self.model.objects.filter(q)                    
            data = ''.join([u'%s|%s|%s\n' % (getattr(f,rel_name),f,f.pk) for f in qs])
        else:
            data = ''
        return djp.http.HttpResponse(data)

