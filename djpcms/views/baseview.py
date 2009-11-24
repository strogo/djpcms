'''
Base class for djpcms views.
'''
import copy

from django.conf import settings
from django import http
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.shortcuts import render_to_response
from django.template import RequestContext, Context, loader
from django.core.exceptions import PermissionDenied


from djpcms.settings import HTML_CLASSES, GRID960_DEFAULT_FIXED, \
                            DEFAULT_TEMPLATE_NAME, DJPCMS_CONTENT_FUNCTION
from djpcms.utils.ajax import jservererror
from djpcms.views.contentgenerator import BlockContentGen
from djpcms.utils.html import grid960
from djpcms.permissions import inline_editing
from djpcms.utils import UnicodeObject, urlbits, urlfrombits, function_module, lazyattr

build_base_context = function_module(DJPCMS_CONTENT_FUNCTION)


# Wrapper around request
class DjpRequestWrap(UnicodeObject):
    '''
    Request wrapper for djpcms views.
    '''
    def __init__(self, request, view, *args, **kwargs):
        self.request  = request
        self.view     = view
        self.css      = HTML_CLASSES
        self._urlargs = None
        self.args     = args
        self.kwargs   = kwargs
        self.wrapper  = None
        self.prefix   = None
    
    def __call__(self, prefix = None, wrapper = None):
        djp = copy.copy(self)
        djp.prefix  = prefix
        djp.wrapper = wrapper
        return djp
    
    @lazyattr
    def get_parent(self):
        p = self.view.parentview(self.request)
        if p:
            return p.requestview(self.request, *self.args, **self.kwargs)
        else:
            return None
    parent = property(get_parent)
    
    @lazyattr
    def get_children(self):
        self.instance
        return self.view.children(self.request, **self.urlargs) or []
    children = property(get_children)
    
    def _get_instance(self):
        instance = self.urlargs.get('instance',None)
        if not instance:
            self.url
            return self.urlargs.get('instance',None)
        else:
            return instance
    def _set_instance(self, instance):
        self.urlargs['instance'] = instance
    instance = property(fget = _get_instance, fset = _set_instance)
    
    def handle_arguments(self):
        if self._urlargs is None:
            i = 0
            urlargs = copy.copy(self.kwargs)
            for arg in self.args:
                i += 1
                urlargs['arg_no_key_%s' % i] = arg
            self._urlargs = urlargs
            self.nargs   = i
        
    def __get_urlargs(self):
        self.handle_arguments()
        return self._urlargs
    urlargs = property(__get_urlargs)
    
    @lazyattr
    def get_url(self):
        '''
        Build the url for this application view
        '''
        return self.view.get_url(self, **self.urlargs)
    url = property(get_url)
        
    @lazyattr
    def get_page(self):
        view    = self.view
        page    = view.get_page()
        self.template = view.get_template(page)
        return page
    page = property(get_page)
        
    def __unicode__(self):
        return unicode(self.view)
    
    def get_linkname(self):
        return self.view.linkname(self.page, **self.urlargs)
    linkname = property(get_linkname)
        
    def get_title(self):
        return self.view.title(self.page, **self.urlargs)
    title = property(get_title)
    
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    def bodybits(self):
        return self.view.bodybits(self.page)
    
    def response(self):
        view    = self.view
        request = self.request
        
        if not view.has_permission(request, self.instance):
            return view.permissionDenied(self)
        
        method  = request.method.lower()
        methods = view.methods(request)
        if method not in (method.lower() for method in methods):
            return http.HttpResponseNotAllowed(methods)
        
        func = getattr(view,'%s_response' % method,None)
        if not func:
            raise ValueError("Allowed view method %s does not exist in %s." % (method,view))
        
        return func(self)
    
    def robots(self):
        if self.view.has_permission():
            return u'ALL'
        else:
            return u'NONE,NOARCHIVE'
        


# THE DJPCMS INTERFACE CLASS for handling views
# the response method handle all the views in djpcms
class djpcmsview(UnicodeObject):
    # This override the template name in the page object (if it exists)
    # hardly used but here just in case.
    template_name = None
    # methods handled by the current view. By default GET and POST only
    _methods      = ('get','post') 
    '''
    Base class for handling django views.
    No views should use this class directly.
    '''
    def requestview(self, request, *args, **kwargs):
        return DjpRequestWrap(request, self, *args, **kwargs)
    
    def get_url(self, djp, **urlargs):
        return None
    
    def get_page(self):
        return None
    
    def methods(self, request):
        '''
        Allowed methods for this view.
        By default it returns the class attribute _methods
        '''
        return self.__class__._methods
    
    def get_template(self,page):
        '''
        given a page objects (which may be None)
        return the template file for the get view
        '''
        if self.template_name:
            return self.template_name
        else:
            if page:
                return page.get_template()
            else:
                return DEFAULT_TEMPLATE_NAME
        
    def title(self, page, **urlargs):
        if page:
            return page.title
        else:
            return None
    
    def linkname(self, page, **urlargs):
        if page:
            return page.link
        else:
            return u'link'
    
    def parentview(self, request):
        pass
    
    def response(self, request, *args, **kwargs):
        djp = self.requestview(request, *args, **kwargs)
        return djp.response()
    
    def render(self, djp, **kwargs):
        return u''
    
    def preget(self, djp):
        pass
    
    def update_content(self, request, c):
        pass
    
    def get_response(self, djp):
        '''
        Handle the GET RESPONSE.
        This function SHOULD NOT be overwritten.
        Several functions can be overwritten for tweaking the results.
        If that is not enough, maybe more hooks should be put in place.
        
        Hooks:
            - 'preget':     for pre-processing and redirect
            - 'render':     for creating content when there is no inner_template
        '''
        #First check for redirect
        re = self.preget(djp)
        if isinstance(re,http.HttpResponse):
            return re
        
        # Get page object and template_name
        request = djp.request
        page    = djp.page
        inner_template  = None
        grid    = self.grid960(page)
        
        # If user not authenticated set a test cookie  
        if not request.user.is_authenticated():
            request.session.set_test_cookie()
        
        c = build_base_context(djp)
        c.update({'djp':  djp, 'grid': grid})
        
        # Inner template available, fill the context dictionary
        # with has many content keys as the number of blocks in the page
        if page and page.inner_template:
            cb = copy.copy(c)
            blocks = page.inner_template.numblocks()
            for b in range(0,blocks):
                cb['content%s' % b] = BlockContentGen(djp, b)
            
            # Call the inner-template renderer
            inner = page.inner_template.render(Context(cb))
            
            if self.editurl:
                b = urlbits(request.path)[1:]
                c['exit_edit_url'] = urlfrombits(b)
            else:
                c['edit_content_url'] = inline_editing(request,self)
             
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.HttpResponse):
                return inner
            
        c['inner'] = inner
        return render_to_response(template_name = djp.template,
                                  context_instance = RequestContext(request, c))
    
    def post_response(self, djp):
        '''
        Handle the post view.
        This function checks the request.POST dictionary
        for a post_view_key specified in HTML_CLASSES (by default 'xhr')
        
        If it finds this key, the post view
        is an AJAX-JSON request and the key VALUE represents
        a function responsible for handling the response.
        
        These ajax enabled post view functions must start with the prefix
        ajax__ followed by the VALUE of the post_view_key.
        
        Example:
            so lets say we find in the POST dictionary
            
            {
            ...
            'xhr': 'change_parameter',
            ...
            }
            
            Than there should be a function called   'ajax__change_parameter'
            which handle the response
        '''
        request   = djp.request
        post      = request.POST
        params    = dict(post.items())
        ajax_key  = params.get(HTML_CLASSES.post_view_key, None)
        def_ajax  = False
        
        # check if this is an ajax request with no ajax_key
        if not ajax_key:
            ajax_key = request.is_ajax()
            def_ajax = True
        else:
            ajax_key = ajax_key.replace('-','_').lower()
        
        # If post_view key is defined, it means this is a AJAX-JSON request
        if ajax_key:
            if def_ajax:
                ajax_view_function = self.default_ajax_view
            else:
                ajax_view = 'ajax__%s' % ajax_key
                ajax_view_function  = getattr(self,str(ajax_view),None)
                
                # No post view function found. Let's try the default ajax post view
                if not ajax_view_function:
                    ajax_view_function = self.default_ajax_view;
            
            try:
                res  = ajax_view_function(djp)
            except Exception, e:
                # we got an error. If in debug mode send a JSON response with
                # the error message back to javascript.
                if settings.DEBUG:
                    res = jservererror(e, url = djp.url)
                else:
                    raise e
            return http.HttpResponse(res.dumps(), mimetype='application/javascript')
        #
        # Otherwise it is a standard POST response
        else:
            return self.default_post(request)
            
    def default_post(self, djp):
        '''
        Default POST view.
        by default we redirect to the next page if available
        otherwise we redirect to home page
        '''
        request   = djp.request
        params    = dict(post.items())
        next      = params.get('next',djp.url)
        return http.HttpResponseRedirect(next)
    
    def default_ajax_view(self, djp):
        '''
        This function is called by the self.post_view method when the
        ajax key is available but no ajax function was found.
        By default it raises an error
        '''
        raise NotImplementedError('Default ajax response not implemented')

    def grid960(self, page):
        if page and page.cssinfo:
            return grid960(columns = page.cssinfo.gridsize, fixed = page.cssinfo.fixed)
        else:
            return grid960()
    
    def has_permission(self, request = None, obj = None):
        '''
        Hook for permissions
        '''
        return True
    
    def in_navigation(self, request, page):
        '''
        Hook for modifying the in_navigation property.
        This default implementation should suffice
        '''
        if page:
            return page.in_navigation
        else:
            return 0
    
    def children(self, request, **kwargs):
        return None
    
    def bodybits(self, page):
        b = u''
        if self.editurl:
            b = u'class="edit"'
        elif page:
            css = page.cssinfo
            if css and css.body_class_name:
                b = 'class="%s"' % css.body_class_name
        return mark_safe(b)
        
    def breadcrumbs(self, final = True):
        '''
        build a breadcrumbs list
        '''
        if self.parent:
            bc = self.parent.breadcrumbs(final = False)
        else:
            bc = []
        return self._addtobreadcrumbs(bc,final)
        
    def _addtobreadcrumbs(self, bc, final):
        me = self.title()
        if final:
            bc.append(me)
        else:
            bc.append(me)
        return bc
    
    def permissionDenied(self, djp):
        raise PermissionDenied
    
    def sortviewlist(self, views):
        def comp(a,b):
            if a.in_navigation() > b.in_navigation():
                return 1
            else:
                return -1
        views.sort(comp)
        return views

class wrapview(djpcmsview):
    '''
    Create a view object that wrap another view object  
    '''
    def __init__(self, view, prefix):
        '''
        @param view: instance of djpcmsview
        @param prefix: String defining the prefix to the view url
        
            let's say view.url = '/some/url/' and prefix = 'edit'
            than the wrpview instance will have a url given by
             '/edit/some/url/'
        '''
        self._view   = view
        self.prefix  = prefix
        self.editurl = None
        
    def __unicode__(self):
        return '%s: %s' % (self.prefix,self._view)
    
    def get_page(self):
        return self._view.get_page()
    
    def get_template(self, page):
        return self._view.get_template(page)
    
    def grid960(self, page):
        return self._view.grid960(page)


class editview(wrapview):
    '''
    Special wrap view for editing page content
    '''
    def __init__(self, view, prefix):
        super(editview,self).__init__(view,prefix)
        self.editurl = self.prefix
    
    def in_navigation(self, request, page):
        return 0
    
    def get_main_nav(self, request):
        return None
