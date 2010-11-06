import operator
from copy import copy
from itertools import izip
from datetime import datetime

from django import http
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.template import loader, RequestContext
from django.utils.text import smart_split
from django.contrib import messages
from django.utils.translation import ugettext as _

from djpcms.conf import settings
from djpcms.forms import saveform
from djpcms.utils.html import Paginator
from djpcms.utils.func import force_number_insert
from djpcms.utils.ajax import jremove, dialog, jredirect
from djpcms.utils import force_unicode, construct_search, isexact
from djpcms.models import Page

from djpcms.views.regex import RegExUrl 
from djpcms.views.cache import pagecache
from djpcms.views.baseview import djpcmsview
from djpcms.core.exceptions import PageNotFound
from djpcms.utils.html import autocomplete


class pageinfo(object):
    
    def __init__(self,url,last_modified):
        self.url = url
        self.last_modified = last_modified


class AppViewBase(djpcmsview):
    '''A :class:`djpcms.views.baseview.djpcmsview` specialised class for application views in :ref:`djpcms applications <topics-applications-index>`.
    
.. attribute:: name
    
    name of view.
    
.. attribute:: parent

    instance of :class:`AppViewBase` or None.
    
.. attribute:: isapp

    if ``True`` the view will be added to the application list and can have its own page object. Default ``False``.
    
.. attribute:: isplugin

    if ``True`` the view can be rendered as :class:`djpcms.plugins.DJPplugin`. Default ``False``.

.. attribute:: in_navigation

    If ``0`` the view won't appear in :ref:`Navigation <topics-included-navigator>`.
    
.. attribute:: plugin_form

    The :attr:`djpcms.plugins.DJPplugin.form` for this view. Default ``None``.
'''
    creation_counter = 0
    plugin_form = None
    _form       = None
    
    def __init__(self,
                 parent     = None,
                 regex      = None,
                 splitregex = False,
                 insitemap  = True,
                 isapp      = False,
                 isplugin   = False,
                 in_navigation = 0,
                 template_name = None,
                 description = None,
                 form        = None,
                 form_withrequest = None):
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
        self._form     = form if form else self.__class__._form
        self._form_withrequest = form_withrequest
        self.creation_counter = AppViewBase.creation_counter
        AppViewBase.creation_counter += 1
        
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
        
    def __get_ajax_response(self, djp):
        # Obsolete
        if self.ajax_views:
            data = djp.request.POST or djp.request.GET
            ajax_key = data.get(settings.HTML_CLASSES.post_view_key, None)
            if ajax_key:
                return self.ajax_views.get(ajax_key,None)
        return None
    
    def isroot(self):
        '''True if this application view represents the root view of the application.'''
        return self.appmodel.root_application is self
    
    def get_form(self, djp, **kwargs):
        return self.appmodel.get_form(djp, self._form,
                                      form_withrequest = self._form_withrequest,
                                      **kwargs)
        
    def is_soft(self, djp):
        page = djp.page
        return False if not page else page.soft_root
        
    def get_page(self, djp):
        pages = pagecache.get_for_application(self.code)
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
                    kwargs.update(dict(izip(self.regex.names,bits)))
                else:
                    for name in names:
                        kwargs.pop(name,None)
        return kwargs
    
    def has_permission(self, request = None, page = None, obj = None):
        if super(AppViewBase,self).has_permission(request, page, obj):
            return self._has_permission(request, obj)
        else:
            return False
        
    def _has_permission(self, request, obj):
        return self.appmodel.has_permission(request, obj)
    
    def render(self, djp, **kwargs):
        '''
        Render the application child.
        This method is reimplemented by subclasses.
        By default it renders the search application
        '''
        pass
    
    def parentresponse(self, djp):
        '''
        Retrive the parent response
        '''
        return self.appmodel.parentresponse(djp, self)
    
    def processurlbits(self, appmodel):
        '''Process url bits and store information for navigation and urls
        '''
        self.appmodel = appmodel
        self.ajax     = appmodel.ajax
        if self.parent:
            self.regex = self.parent.regex + self.urlbit
        else:
            self.regex = self.urlbit
            
    def __deepcopy__(self, memo):
        return copy(self)  
    
    
class AppView(AppViewBase):
    '''An :class:`AppViewBase` class for views in :class:`djpcms.views.appsite.ModelApplication`.
    '''
    def __init__(self, isapp = True, splitregex = True, **kwargs):
        super(AppView,self).__init__(isapp = isapp,
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
    
    def basequery(self, request, **kwargs):
        '''Base query for application.
If this is the root view (no parents) it returns
:func:`djpcms.views.appsite.ModelApplication.basequery`, otherwise
it returns the :func:`appquery` of the :func:`modelparent` view.
        '''
        if self.modelparent():
            return self.parent.appquery(request)
        else:
            return self.appmodel.basequery(request)
    
    def appquery(self, request, *args, **kwargs):
        '''This function implements the application query.
By default return the :func:`basequery` (usually all items of a model).'''
        return self.basequery(request)
    
    def permissionDenied(self, djp):
        return self.appmodel.permissionDenied(djp)
    
    def sitemapchildren(self):
        return [] 
    
    
class SearchView(AppView):
    '''An :class:`AppView` class for searching objects in model. By default :attr:`AppViewBase.in_navigation` is set to ``True``.
    '''
    search_text = 'search_text'
    '''identifier for queries. Default ``search_text``.'''
    
    def __init__(self, in_navigation = True, **kwargs):
        super(SearchView,self).__init__(in_navigation=in_navigation,**kwargs)
    
    def appquery(self, request, *args, **kwargs):
        '''This function implements the search query.
The query is build using the search fields specifies in
:attr:`djpcms.views.appsite.ModelApplication.search_fields`.
It returns a queryset.
        '''
        qs = self.basequery(request)
        
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
    
    def render(self, djp, **kwargs):
        '''Perform the custom query over the model objects and return a paginated result
        '''
        request  = djp.request
        appmodel = self.appmodel
        if kwargs:
            urlargs = djp.kwargs
            urlargs.update(kwargs)
            djp = self(request, **urlargs)
        query = self.appquery(request, *djp.args, **djp.kwargs)
        p  = Paginator(request, query, per_page = appmodel.list_per_page)
        c  = copy(djp.kwargs)
        c.update({'paginator': p,
                  'djp': djp,
                  'url': djp.url,
                  'model': self.model,
                  'css': appmodel.ajax,
                  'appmodel': appmodel,
                  'headers': appmodel.list_display})
        if p.qs:
            c['items'] = self.appmodel.data_generator(djp, p.qs)
            
        return loader.render_to_string(['components/pagination.html',
                                        'djpcms/components/pagination.html'],
                                        c)    


class AddView(AppView):
    '''An :class:`AppView` class which renders a form for adding instances
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
    
    def render(self, djp, **kwargs):
        return self.get_form(djp, **kwargs).render(djp)
    
    def default_post(self, djp):
        return saveform(djp)

            
class ObjectView(AppView):
    '''An :class:`AppView` class view for model instances.
A view of this type has an embedded object available which is used to generate the full url.'''
    object_view = True
    
    def get_url(self, djp, instance = None, **kwargs):
        if instance:
            kwargs.update(self.appmodel.objectbits(instance))
        else:
            instance = self.appmodel.get_object(djp.request, **kwargs)
        
        if not instance:
            raise http.Http404
        
        djp.instance = instance
        return super(ObjectView,self).get_url(djp, **kwargs)
    
    
    def title(self, page, instance = None, **kwargs):
        return self.appmodel.title_object(instance)
    

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
    
    def default_post(self, djp):
        instance = djp.instance
        try:
            bid = self.appmodel.remove_object(instance)
            if bid:
                return jremove('#%s' % bid)
            else:
                pass
        except Exception, e:
            raise ValueError('Could not remove %s: %s' % (instance,e))
      

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
    
    def render(self, djp, **kwargs):
        return self.get_form(djp, **kwargs).render(djp)
    
    def save(self, request, f):
        return self.appmodel.object_from_form(f)
    
    def ajax__save(self, djp):
        '''
        Save and redirect to default redirect
        '''
        return self.default_post(djp,True)
    
    def ajax__save_and_continue(self, djp):
        '''
        Save and redirect to default redirect
        '''
        return self.default_post(djp,False)
    
    def default_post(self, djp):
        return saveform(djp,True)

    def defaultredirect(self, djp):
        return self.appmodel.viewurl(djp.request, djp.instance) or djp.url

    
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
            raise http.Http404
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
        return http.HttpResponse(data)

