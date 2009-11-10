from django.conf import settings
from django.db import models
from django.utils.safestring import mark_safe
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.contrib.contenttypes.models import ContentType

from djpcms.settings import HTML_CLASSES, POST_ERROR_TEMPLATE, GRID960_DEFAULT_FIXED
from djpcms.db.interfaces import getobject, unique_code_value
from djpcms.models import Page, JavaScript
from djpcms.html import TemplatePlugin, htmlfactory, breadcrumbs, grid960, view_navigation
from djpcms.utils import lazyattr
from djpcms.views.wrapview import djpcmsview

import cache


__all__ = ['baseview',
           'badview',
           'modelview',
           'modelurl',
           'default_navigation_constructor']
    

def default_navigation_constructor(request, view, nav_func, children):
    parentview = view.parentview
    if parentview:
        if children:
            children.append(view.url)
        else:
            children = [view.url]
        func = getattr(parentview,nav_func)
        return func(request, children = children)
    else:
        return view_navigation(request = request, view = view, urlselects = children)


def create_view(obj,
                dbmodel,
                args,
                edit    = None,
                child   = None,
                factory = None,
                **kwargs):
    '''
    view object constructor
        @param dbmodel: the database model for the Page
        @param args:    list of arguments
        @param output_args:   a list or None
        @param edit:    string (Optional)
    '''
    obj.page          = dbmodel
    obj.gridcolumns   = kwargs.pop('grid_columns',12)
    obj.grid_fixed    = kwargs.pop('grid_fixed',GRID960_DEFAULT_FIXED)
    obj.editurl       = edit
    obj._children     = []
    ct = obj.page.content_type
    if ct:
        obj.model = ct.model_class()
    else:
        obj.model = None
    obj.object    = None
    if child:
        obj._child     = child
        if child.template_name:
            obj.template_name = child.template_name
        
    if factory:
        obj.factory = factory
    obj.url = obj.make_url(obj.processargs(args))
    return obj



class baseview(djpcmsview):
    '''
    Base class for django views
    This class is responsible for handling GET and POST views associated with a Page
    
    Children caching
    The view object caches children in order to avoid to hit the database all around the place.
    '''
    authflag      = None
    
    def __new__(cls, *args, **kwargs):
        return create_view(super(baseview, cls).__new__(cls), *args, **kwargs)
        
    def processargs(self, args):
        '''
        Process arguments tuple.
        Arguments are string or model objects used to calculate the url.
        '''
        p = self._make_parent_view(args)
        self.parentview = p
        oargs = self.preprocess_for_object(args)
        self.get_object(oargs)
        return oargs
    
    def preprocess_for_object(self, args):
        '''
        Handle the argument list.
        @param args: list or tuple of arguments 
        '''
        if args:
            N = self.page.num_relative_arguments()
            pargs   = args[:N]
            for i in range(0,N):
                args.pop(0)
            return pargs
        else:
            return []
        
    def _make_parent_view(self, args):
        '''
        Create the parent view object and return the number of arguments
        for the current view
        '''
        pa    = self.page.parent
        if not pa:
            return None
        else:
            number_of_parent_arguments = pa.num_arguments()
            pargs   = args[:number_of_parent_arguments]
            for i in range(0,number_of_parent_arguments):
                args.pop(0)
            return self._get_parent_view(pargs)
        
    def grid960(self):
        return grid960(self.gridcolumns,self.grid_fixed)
    
    def _get_parent_view(self, args):
        return cache.view_from_page(self.page.parent, args)
    
    def make_url(self, args):
        '''
        Create the view url
        '''
        if not self.parentview:
            return '/'
        
        url = self.page.modified_url_pattern()
        if args:
            try:
                url = url % tuple(args)
            except Exception, e:
                raise Http404(str(e))
            
        pview = self.parentview
        if pview:
            return '%s%s/' % (self.parentview.url,url)
        else:
            return '/%s/' % url
    
    def num_arguments(self):
        return self.page.num_arguments()
    
    def get_object(self, args):
        '''
        This function handle the remaining arguments in the url.
        This function can be overritten by derived classes.
        By default it handle only one entry and try to retrive
        the database object.
        
        @param args: list or tuple of arguments
        @return: list of url bits for the object 
        '''
        if args:
            self.object = getobject(self.model,args[0])
            
    def object_url(self, obj):
        '''
        Create the relative url for object obj.
        This function can be overritten by views to customize the
        object url.
        '''
        return str(unique_code_value(obj))
    
    def breadcrumbs(self):
        '''
        Build bread crumbs for current page
        '''
        p = self.bread_crumbs_parent()
        if not p:
            return None
        
        b = breadcrumbs()
        b.addlistitem(self.bread_crumbs_name())
        while p:
            b.addlistitem(p.bread_crumbs_name(), url = p.url)
            p = p.bread_crumbs_parent()
        b.reverse()
        return b
    
    def bread_crumbs_parent(self):
        '''
        Breadcrumbs parent by default is the parentview.
        However, sometimes you may whant to change this default.
        '''
        return self.parentview
        
    def bread_crumbs_name(self):
        '''
        String to display in bread-crumbs element.
        By default it is the urldisplal function.
        This can be changed
        '''
        return self.urldisplay()
            
    def urldisplay(self):
        if self.object:
            return str(self.object)
        else:
            return self.page.href_name
        
    def title(self):
        return self.page.title    
        
    def get_main_nav(self, request, children = None):
        '''
        Get the main navigation for the page.
        The default implementation is to look for the parent
        main navigation.
        If this view requires a brand new main navigation
        than this function should be re-implemented.
        '''
        return default_navigation_constructor(request,self,'get_main_nav',children)
        
    def get_page_nav(self, request, children = None):
        '''
        The page navigation. By default it return a list of dictionary of
        children pages.
        '''
        return list(self.page.children_pages.filter(in_navigation = True))
    
    def scripts(self):
        return self.page.scripts().values()
    
    def end_scripts(self):
        return self.page.end_scripts().values()
    
    def remove_script(self,code):
        scr = self.page.scripts()
        try:
            scri = JavaScript.objects.get(code = code)
            scr.pop(scri.order,None)
        except:
            pass
        return scr.itervalues()
    
    def factoryurl(self, *args):
        '''
        '''
        factory = self.page.object()
        if factory.url == self.url:
            return self.url
        else:
            return factory.factoryurl(*args)
        
    def process(self, func = None):
        '''
        This function can be called to process a form in post view.
        TODO: Looks like this function is obsolete
        '''
        f = self.create_element()
        if f.is_valid():
            cdata = f.cleaned_data
            fun   = func or self.process_data
            return fun(f, cdata)
        else:
            return f.jerrors
    
    def has_permission(self, request):
        if self.model and self.authflag:
            opts = self.model._meta
            p = '%s.%s_%s' % (opts.app_label,self.authflag,opts.module_name)
            return request.user.has_perm(p)
        else:
            return True
    
    def permission_denied(self):
        return TemplatePlugin(template = 'djpcms/components/permission_denied.html').render()
    
    def meta_content_type(self):
        return mark_safe(u'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
    
    def meta_content_lang(self):
        return mark_safe(u'<meta http-equiv="Content-Language" content="en-uk" />')
    
    def meta_description(self):
        return ""
    
    def safeurl(self, aview):
        try:
            return aview.url
        except:
            return None
        
    def incache(self):
        return True
    

def modelview(object, request, subview = None):
    opt = object._meta
    ct = ContentType.objects.get(app_label = opt.app_label,
                                 model = opt.module_name)
    page = Page.objects.filter(content_type = ct)
    if page.count():
        page = page[0]
        fview = cache.view_from_page(page)
        if subview:
            if isinstance(object,models.Model):
                obj = (object,)
            else:
                obj = ()
            return fview.newchildview(request, subview, *obj)
    else:
        return None



class badview(djpcmsview):
    
    def __init__(self, request, template_name, httpresponse, gridcolumn = 12):
        self.page          = Page.objects.root()
        self.editurl       = None
        self.model         = None
        self.gridcolumn    = gridcolumn
        self.template_name = template_name
        self._httpresponse = httpresponse
        self.url           = request.path
        
    def get_main_nav(self, request):
        return None

    def view_contents(self, request, params):
        pass
    
    def render_to_response(self, template_name = None, context_instance = None):
        t = loader.get_template(template_name)
        return self._httpresponse(t.render(context_instance))





    
def modelurl(object, request, subview = None):
    view = modelview(object, request, subview)
    if view:
        return view.url
    else:
        return None