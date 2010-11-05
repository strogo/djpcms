'''
Base class for djpcms views.
'''
import copy

from django import http
from django.template import RequestContext, Context, loader
from django.core.exceptions import PermissionDenied
from django.forms import Media, MediaDefiningClass


from djpcms.conf import settings
from djpcms.permissions import inline_editing, get_view_permission, has_permission
from djpcms.contrib import messages
from djpcms.utils.ajax import jservererror, jredirect
from djpcms.utils.html import grid960, submit
from djpcms.forms.cms import ShortPageForm, NewChildForm
from djpcms.utils.uniforms import UniForm
from djpcms.utils import UnicodeObject, urlbits, urlfrombits, function_module, \
                         htmltype, mark_safe, force_unicode

from djpcms.views.cache import pagecache
from djpcms.views.response import DjpResponse
from djpcms.views.contentgenerator import BlockContentGen


# THE DJPCMS INTERFACE CLASS for handling views
# the response method handle all the views in djpcms
class djpcmsview(UnicodeObject):
    '''Base class for handling ``urls`` requests.
    
    .. attribute:: _methods

        Tuple of request methods handled by ``self``. By default ``GET`` and ``POST`` only::
        
            _methods = ('get','post')
    '''
    template_name = None
    '''Used to override the template name in the :class:`djpcms.models.Page` model instance (if it exists).
Not used very often but here just in case.'''
    parent        = None
    '''The parent view of ``self``. An instance of :class:`djpcmsview` or ``None``'''
    purl          = None
    
    object_view = False
    
    _methods      = ('get','post')

    def get_media(self):
        return Media()
    
    def names(self):
        return None
    
    def get_url(self, djp, **urlargs):
        return djp.request.path
    
    def get_page(self, djp):
        '''The :class:`djpcms.models.Page` instances associated with this view.'''
        return None
    
    def is_soft(self, djp):
        return not self.parentresponse(djp)
    
    def __call__(self, request, *args, **kwargs):
        return DjpResponse(request, self, *args, **kwargs)
    
    def methods(self, request):
        '''Allowed request methods for this view.
        By default it returns :attr:`_methods`.
        '''
        return self.__class__._methods
    
    def get_template(self, page = None):
        '''Given a :class:`djpcms.models.Page` instance *page*, which may be ``None``,
returns the template file for the ``GET`` response. If :attr:`template_name` is specified,
it uses it, otherwise if *page* is available, it gets the template from
:meth:`djpcms.models.Page.get_template`.
If *page* is ``None`` it returns :setting:`DEFAULT_TEMPLATE_NAME`.'''
        if self.template_name:
            return self.template_name
        else:
            if page:
                return page.get_template()
            else:
                return settings.DEFAULT_TEMPLATE_NAME
        
    def title(self, page, **urlargs):
        '''View title.'''
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
    
    def specialkwargs(self, page, kwargs):
        return kwargs
    
    def render(self, djp, **kwargs):
        '''
        Render the Current View plugin.
        Return safe unicode
        This function is implemented by application views
        '''
        return u''
    
    def preget(self, djp):
        pass
    
    def extra_content(self, djp, c):
        pass
    
    def handle_response(self, djp):
        '''Handle the RESPONSE.This function SHOULD NOT be overwritten.
Several functions can be overwritten for tweaking the results.
If that is not enough, maybe more hooks should be put in place.
Hooks:
* 'preget':     for pre-processing and redirect
* 'render':     for creating content when there is no inner_template
* *extra_response*: for more.'''
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
        
        context = {'grid': grid}
        
        # Inner template available, fill the context dictionary
        # with has many content keys as the number of blocks in the page
        if page:
            context['htmldoc'] = htmltype.get(page.doctype)
        else:
            context['htmldoc'] = htmltype.get()
            
        if page:
            if not self.editurl and djp.has_own_page():
                context['edit_content_url'] = inline_editing(request,page,djp.instance)
            
        if page and page.inner_template:
            cb = {'djp':  djp,
                  'grid': grid}
            blocks = page.inner_template.numblocks()
            for b in range(0,blocks):
                cb['content%s' % b] = BlockContentGen(djp, b)
            
            # Call the inner-template renderer
            inner = page.inner_template.render(Context(cb))
        else:
            # No page or no inner_template. Get the inner content directly
            inner = self.render(djp)
            if isinstance(inner,http.HttpResponse):
                return inner
        
        context['inner'] = inner
        self.extra_content(djp,context)
        return djp.render_to_response(context)
    
    def get_ajax_response(djp):
        return None
    
    def get_response(self, djp):
        return self.handle_response(djp)
    
    def default_post(self, djp):
        raise NotImplementedError('Default Post view not implemented')
    
    def post_response(self, djp):
        '''Handle the post view. This function checks the request.POST dictionary
for a post_view_key specified in HTML_CLASSES (by default 'xhr')
        
If it finds this key, the post view is an AJAX-JSON request and the key VALUE represents
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
which handle the response'''
        request   = djp.request
        post      = request.POST
        is_ajax   = request.is_ajax()
        ajax_key  = False
        mimetype  = None
        
        if is_ajax:
            mimetype = 'application/javascript'
            params   = dict(post.items())
            ajax_key = params.get(settings.HTML_CLASSES.post_view_key, None)
            if ajax_key:
                ajax_key = ajax_key.replace('-','_').lower()
            
        # If ajax_key is defined, it means this is a AJAX-JSON request
        if is_ajax:
            #
            # Handle the cancel request redirect.
            # Check for next in the parameters, If not there redirect to self.defaultredirect
            if ajax_key == 'cancel':
                url = params.get('next',None)
                if not url:
                    url = self.defaultredirect(djp)
                res = jredirect(url)
            else:
                ajax_view_function = None
                if ajax_key:
                    ajax_view = 'ajax__%s' % ajax_key
                    ajax_view_function  = getattr(self,str(ajax_view),None)
                
                # No post view function found. Let's try the default ajax post view
                if not ajax_view_function:
                    ajax_view_function = self.default_post;
            
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
        # Otherwise it is the default POST response
        else:
            return self.default_post(djp)


    def grid960(self, page = None):
        if page and page.cssinfo:
            return grid960(columns = page.cssinfo.gridsize, fixed = page.cssinfo.fixed)
        else:
            return grid960()
    
    def has_permission(self, request = None, page = None, obj = None):
        '''Check if view can be displayed.
        '''
        if request and page:
            return has_permission(request.user,get_view_permission(page),page)
        else:
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
    
    def contentbits(self, page):
        b = u''
        if page:
            css = page.cssinfo
            if css and css.container_class_name:
                b = ' class="%s"' % css.container_class_name
        return mark_safe(b)
    
    def permissionDenied(self, djp):
        raise PermissionDenied
    
    def defaultredirect(self, djp):
        return djp.url
    
    def children(self, djp, instance = None, **kwargs):
        '''Return children permitted views for self.
It includes views not in navigation. In scanning for children we porposefully
leave a possible object instance out of the key-values arguments.
If we didn't do that, test_navigation.testMultiPageApplication would fail.'''
        views = []
        page  = djp.page
        request = djp.request
        if not page:
            return views
        
        pchildren = pagecache.get_children(page)
        
        for child in pchildren:
            try:
                cview = pagecache.view_from_page(request, child)
            except Exception, e:
                continue
            if cview.has_permission(request):
                cdjp = cview(request, **cview.specialkwargs(child,kwargs))
                if isinstance(cdjp,DjpResponse):
                    try:
                        cdjp.url
                    except:
                        pass
                    else:
                        views.append(cdjp)
        return views
    
    def redirect(self, url):
        '''Shortcut function for redirecting to *url*.'''
        return http.HttpResponseRedirect(url)


class pageview(djpcmsview):
    
    def __init__(self, page):
        self.page    = page
        self.editurl = None  

    def __unicode__(self):
        return self.page.url
        
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def get_page(self, djp, **kwargs):
        return self.page
    
    def is_soft(self, djp):
        return self.page.soft_root


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
    
    def get_page(self, djp):
        return self._view.get_page(djp)
    
    def get_template(self, page):
        return self._view.get_template(page)
    
    def grid960(self, page):
        return self._view.grid960(page)


class editview(wrapview):
    '''Special :class:`djpcms.views.baseview.wrapview` for editing page content.
This view is never in navigation and it provides a hook for adding the edit page form.
    '''
    def __init__(self, view, prefix):
        super(editview,self).__init__(view,prefix)
        self.editurl = self.prefix
    
    def in_navigation(self, request, page):
        return 0
    
    def has_permission(self, request = None, page = None, obj = None):
        if self._view.has_permission(request,page,obj):
            return inline_editing(request, page, obj)
        else:
            return False  
    
    def extra_content(self, djp, c):
        uni = UniForm(ShortPageForm(instance = djp.page), action = djp.url)
        uni.inputs.append(submit(value = "change", name = '_save'))
        c['page_form'] = uni.render()
        uni = UniForm(NewChildForm(), action = djp.url)
        uni.inputs.append(submit(value = "create", name = '_child'))
        c['new_child_form'] = uni.render()
        c['page_url'] = self.page_url(djp.request)

    def default_post(self, djp):
        request = djp.request
        data = dict(request.POST.items())
        if data.get('_child',None) == 'create':
            f = NewChildForm(data = request.POST, response = djp)
            if f.is_valid():
                page = f.save()
                messages.info(request, 'Page %s created' % page)
            else:
                return self.handle_response(djp)
        else:
            f = ShortPageForm(instance = djp.page, data = request.POST)
            if f.is_valid():
                page = f.save()
                messages.info(request, 'Page %s updated' % page)
            else:
                return self.handle_response(djp)
        pagecache.clear(request)
        return self.redirect(djp.url)
    
    def page_url(self, request):
        return urlfrombits(urlbits(request.path)[1:])
