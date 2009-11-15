'''
Base class for djpcms views.
'''
from django.conf import settings
from django import http
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.core.exceptions import PermissionDenied

from djpcms.settings import HTML_CLASSES, GRID960_DEFAULT_FIXED, DEFAULT_TEMPLATE_NAME
from djpcms.utils.ajax import jservererror
from djpcms.views.contentgenerator import BlockContentGen
from djpcms.html import TemplatePlugin, breadcrumbs, grid960
from djpcms.utils import UnicodeObject
from djpcms.views.navigation import default_navigation_constructor
from djpcms.permissions import inline_editing
from djpcms.utils import urlbits, urlfrombits

from djpcms.views.load import *


class ResponseBase(UnicodeObject):
    '''
    Generic response based on djpcms view objects
    '''
    def __init__(self, request, view, *args, **kwargs):
        self.request  = request
        self.view     = view
        self.page     = view.get_page()
        self.template = view.get_template(self.page)
        self.css      = HTML_CLASSES
        try:
            self.object = view.object
        except:
            self.object = None
        self.args    = args
        self.kwargs  = kwargs
        
    def __unicode__(self):
        return unicode(self.view)
    
    def urlname(self):
        '''
        String to display as text in a link tag
        '''
        if self.page:
            return self.page.href_name
        else:
            return self.title()
        
    def title(self):
        if self.page:
            title = self.page.title
        else:
            title = None
        return self.view.title(self.request, title)
    
    def in_navigation(self):
        if self.page:
            return self.page.in_navigation
        else:
            return 1
    
    def __getattr__(self, name):
        global _Custom_response_methods
        attr = getattr(self.view,name,None)
        if attr and callable(attr):
            # First we try using request as argument
            try:
                return self.get_view_attr(attr)
            except:
                return attr()
        else:
            return attr
        
    def get_view_attr(self, attr):
        return attr(self.request)


class djpcmsview(UnicodeObject):
    # This override the template name in the page object (if it exists)
    template_name = None
    _methods      = ('get','post') 
    '''
    Base class for handling django views.
    No views should use this class directly.
    '''
    
    def requestview(self, request):
        return ResponseBase(request, self)
    
    def get_url(self, request, *args):
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
        
    def title(self, request, pagetitle):
        return pagetitle
    
    def get_main_nav(self, request, children = None):
        '''
        Get the main navigation for the page.
        The default implementation is to look for the parent
        main navigation.
        If this view requires a brand new main navigation
        than this function should be re-implemented.
        '''
        return default_navigation_constructor(request, self, 'get_main_nav', children)
    
    def get_page_nav(self, request):
        return None
    
    def parentview(self, request):
        pass
    
    def response(self, request, *args, **kwargs):
        '''
        Entry point.
        NO NEED TO OVERRIDE THIS FUNCTION
        '''
        # we do one more final check for permission
        if not self.has_permission(request):
            raise PermissionDenied
        
        method  = request.method.lower()
        methods = self.methods(request)
        if method not in (method.lower() for method in methods):
            return http.HttpResponseNotAllowed(methods)
        
        view = self.handle_reponse_arguments(request,*args,**kwargs)
        
        func = getattr(view,'%s_response' % method,None)
        if not func:
            raise ValueError("Allowed view method %s does not exist in %s." % (method,view))
        
        return func(request)
        
    def handle_reponse_arguments(self, request, *args, **kwargs):
        '''
        Handle response arguments
        By default return self
        '''
        return self
    
    def preget(self, request):
        pass
    
    def update_content(self, request, c):
        pass
    
    def get_response(self, request):
        '''
        Handle the Get view.
        This function SHOULD NOT be overwritten.
        Several functions can be reimplemented for twicking the result.
        In particular:
            - 'preget' for some sort of preprocessing (and redirect)
            - 'update_content' - for creating content when there is no inner_template
        '''
        #First check for redirect
        re = self.preget(request)
        if isinstance(re,http.HttpResponse):
            return re
        
        cl = self.requestview(request)
        
        # Get page object and template_name
        page = cl.page
        inner_template  = None
        
        # If user not authenticated set a test cookie  
        if not request.user.is_authenticated():
            request.session.set_test_cookie()
               
        c = {'cl':               cl,
             'sitenav':          self.get_main_nav(request),
             'grid':             self.grid960()}
        
        # Inner template available, fill the context dictionary
        # with has many content keys as the number of blocks in the page
        if page and page.inner_template:
            cb = {'cl': cl,
                  'grid': self.grid960()}
            blocks = page.inner_template.numblocks()
            for b in range(0,blocks):
                cb['content%s' % b] = BlockContentGen(cl, b)
                    
            inner = page.inner_template.render(RequestContext(request, cb))
            
            if self.editurl:
                b = urlbits(request.path)[1:]
                c['exit_edit_url'] = urlfrombits(b)
            else:
                c['edit_content_url'] = inline_editing(request,self)
             
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.inner_content(request)
            
        c['inner'] = inner
        return self.render_to_response(template_name = cl.template,
                                       context_instance = RequestContext(request, c))
    
    def post_response(self, request):
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
        post      = request.POST
        params    = dict(post.items())
        ajax_key  = params.get(HTML_CLASSES.post_view_key, None)
        
        # If post_view key is defined, it means this is a AJAX-JSON request
        if ajax_key:
            ajax_key = ajax_key.replace('-','_').lower()
            try:
                ajax_view = 'ajax__%s' % ajax_key
                ajax_view_function  = getattr(self,str(ajax_view),None)
                
                # No post view function found. Let's try the default ajax post view
                if not ajax_view_function:
                    ajax_view_function = self.default_ajax_view;
                    
                res  = ajax_view_function(request)
            except Exception, e:
                # we got an error. If in debug mode send a JSON response with
                # the error message back to javascript.
                if settings.DEBUG:
                    res = jservererror(e, url = self.url)
                else:
                    raise e
            return http.HttpResponse(res.dumps(), mimetype='application/javascript')
        #
        # Otherwise it is a standard POST response
        else:
            return self.default_post(request)
            
    def default_post(self, request):
        '''
        Default POST view.
        by default we redirect to the next page if available
        otherwise we redirect to home page
        '''
        params = dict(post.items())
        next   = params.get('next',self.url)
        return http.HttpResponseRedirect(next)
    
    def default_ajax_view(self, request):
        '''
        This function is called by the self.post_view method when the ajax is is available
        but no ajax function was found.
        By default it raises an error
        '''
        raise NotImplementedError('Default ajax response not implemented')

    def grid960(self):
        return grid960()
    
    def render_to_response(self, template_name = None, context_instance = None): 
        return render_to_response(template_name    = template_name,
                                  context_instance = context_instance)
    
    def has_permission(self, request):
        return True
    
    def bodybits(self):
        if self.editurl:
            return mark_safe(u'class="edit"')
        else:
            return u''
        
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
    
    def grid960(self):
        return self._view.grid960()


class editview(wrapview):
    '''
    Special wrap view for editing page content
    '''
    def __init__(self, view, prefix):
        super(editview,self).__init__(view,prefix)
        self.editurl = self.prefix
        
    def get_main_nav(self, request):
        return None
