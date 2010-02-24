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
from djpcms.utils.ajax import jservererror, jredirect
from djpcms.utils.html import grid960
from djpcms.permissions import inline_editing
from djpcms.utils import UnicodeObject, urlbits, urlfrombits, function_module, htmltype

from djpcms.views.cache import pagecache
from djpcms.views.response import DjpResponse
from djpcms.views.contentgenerator import BlockContentGen

more_content = lambda djp : {}
build_base_context = function_module(DJPCMS_CONTENT_FUNCTION, more_content)



# THE DJPCMS INTERFACE CLASS for handling views
# the response method handle all the views in djpcms
class djpcmsview(UnicodeObject):
    # This override the template name in the page object (if it exists)
    # hardly used but here just in case.
    template_name = None
    parent        = None
    purl          = None
    # methods handled by the current view. By default GET and POST only
    _methods      = ('get','post') 
    '''
    Base class for handling django views.
    No views should use this class directly.
    '''    
    def get_url(self, djp, **urlargs):
        return None
    
    def get_page(self):
        return None
    
    def __call__(self, request, *args, **kwargs):
        return DjpResponse(request, self, *args, **kwargs)
    
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
    
    def linkname(self, djp):
        page = djp.page
        if page:
            return page.link
        else:
            return u'link'
    
    def parentresponse(self, djp):
        if djp.page.parent:
            view = pagecache.view_from_page(djp.request, djp.page.parent)
            return view(djp.request)
        else:
            return None
    
    def render(self, djp, **kwargs):
        return u''
    
    def preget(self, djp):
        pass
    
    def update_content(self, request, c):
        pass
    
    def handle_response(self, djp):
        '''
        Handle the RESPONSE.
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
        if not request.user.is_authenticated() and request.method == 'GET':
            request.session.set_test_cookie()
        
        more_content = build_base_context(djp)
        more_content['grid'] = grid
        
        # Inner template available, fill the context dictionary
        # with has many content keys as the number of blocks in the page
        if page:
            more_content['htmldoc'] = htmltype.get(page.doctype)
        else:
            more_content['htmldoc'] = htmltype.get()
            
        if page and page.inner_template:
            cb = {'djp':  djp, 'grid': grid}
            blocks = page.inner_template.numblocks()
            for b in range(0,blocks):
                cb['content%s' % b] = BlockContentGen(djp, b)
            
            # Call the inner-template renderer
            inner = page.inner_template.render(Context(cb))
            
            if self.editurl:
                b = urlbits(request.path)[1:]
                more_content['exit_edit_url'] = urlfrombits(b)
            else:
                more_content['edit_content_url'] = inline_editing(request,self)
             
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.HttpResponse):
                return inner
            
        more_content['inner'] = inner
        return djp.render_to_response(more_content)
    
    def get_response(self, djp):
        return self.handle_response(djp)
    
    def default_post(self, djp):
        return self.handle_response(djp)
    
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
            #
            # Handle the cancel request redirect.
            # Check for next in the parameters, If not there redirect to self.defaultredirect
            if ajax_key == 'cancel':
                url = params.get('next',None)
                if not url:
                    url = self.defaultredirect(djp)
                res = jredirect(url)
            else:    
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
            return self.default_post(djp)
    
    def default_ajax_view(self, djp):
        '''
        This function is called by the self.post_view method when the
        ajax key is available but no ajax function was found.
        By default it raises an error
        '''
        raise NotImplementedError('Default ajax response not implemented')

    def grid960(self, page = None):
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
    
    def bodybits(self, page):
        b = u''
        if self.editurl:
            b = u'class="edit"'
        elif page:
            css = page.cssinfo
            if css and css.body_class_name:
                b = 'class="%s"' % css.body_class_name
        return mark_safe(b)
    
    def permissionDenied(self, djp):
        raise PermissionDenied
    
    def defaultredirect(self, djp):
        return djp.url
    
    def children(self, request, **kwargs):
        '''
        Return children permitted views for self.
        It includes views not in navigation
        '''
        views = []
        page      = self.get_page()
        if not page:
            return views
        
        pchildren = pagecache.get_children(page)
        
        for child in pchildren:
            try:
                cview = pagecache.view_from_page(request, child)
            except Exception, e:
                continue
            if cview.has_permission(request):
                djp = cview(request, **kwargs)
                if isinstance(djp,DjpResponse):
                    views.append(djp)
        return views


class pageview(djpcmsview):
    
    def __init__(self, page):
        self.page    = page
        self.editurl = None  

    def __unicode__(self):
        return self.page.url
    
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def get_page(self):
        return self.page
    
    def has_permission(self, request = None, obj = None):
        if self.page.requires_login:
            if request:
                return request.user.is_authenticated()
            else:
                return False
        else:
            return True    


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
    
