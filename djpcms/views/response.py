import copy

from django import http
from django.shortcuts import render_to_response
from django.template import RequestContext

from djpcms.conf import settings
from djpcms.template import Template, Context
from djpcms.utils import lazyattr, mark_safe, smart_str
from djpcms.utils.navigation import Navigator, Breadcrumbs


class DjpResponse(http.HttpResponse):
    '''
    Lazy HttpResponse Class
    '''
    def __init__(self, request, view, *args, **kwargs):
        '''
        @param request: instance of HttpRequest
        @param view: instance of djpcmsview  
        '''
        super(DjpResponse,self).__init__()
        self._container = None
        self.request    = request
        self.view       = view
        self.css        = settings.HTML_CLASSES
        self._urlargs   = None
        self.args       = args
        self.kwargs     = kwargs
        self.wrapper    = None
        self.prefix     = None
        self.media      = view.get_media()
        self._plugincss = {}
    
    def __repr__(self):
        return self.url
    
    def __str__(self):
        return self.url
    
    def __call__(self, prefix = None, wrapper = None):
        djp = copy.copy(self)
        djp.prefix  = prefix
        djp.wrapper = wrapper
        return djp
    
    def get_linkname(self):
        return self.view.linkname(self)
    linkname = property(get_linkname)
        
    def get_title(self):
        return self.view.title(self.page, **self.urlargs)
    title = property(get_title)
    
    def bodybits(self):
        return self.view.bodybits(self.page)
    
    def set_content_type(self, ct):
        h = self._headers['content-type']
        h[1] = ct
        
    @lazyattr
    def in_navigation(self):
        return self.view.in_navigation(self.request, self.page)
    
    @lazyattr
    def _get_page(self):
        '''
        Get the page object
        '''
        return self.view.get_page()
    page = property(_get_page)
    
    @lazyattr
    def get_url(self):
        '''
        Build the url for this application view
        '''
        return self.view.get_url(self, **self.urlargs)
    url = property(get_url)
    
    @lazyattr
    def _get_template(self):
        return self.view.get_template(self.page)
    template_file = property(_get_template)
    
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
    
    @lazyattr
    def _get_parent(self):
        '''
        Parent Response object
        '''
        return self.view.parentresponse(self)
    parent = property(_get_parent)
    
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
    
    def robots(self):
        '''
        Robots
        '''
        if self.view.has_permission(None, self.instance):
            if not self.page or self.page.insitemap:
                return u'ALL'
        return u'NONE,NOARCHIVE'
        
    def response(self):
        '''
        return the type of response or an instance of HttpResponse
        '''
        view    = self.view
        request = self.request
        
        # Last check for permissions
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
        
        
    
    def render_to_response(self, more_context = None, **kwargs):
        """
        A shortcut method that runs the `render_to_response` Django shortcut.
 
        It will apply the view's context object as the context for rendering
        the template. Additional context variables may be passed in, similar
        to the `render_to_response` shortcut.
 
        """
        context  = RequestContext(self.request)
        d = context.push()
        if more_context:
            d.update(more_context)
        d.update({'djp':        self,
                  'media':      self.media,
                  'page':       self.page,
                  'cssajax':    self.css,
                  'plugincss':  self.get_plugincss(),
                  'is_popup':   False,
                  'admin_site': False,
                  'sitenav':    Navigator(self)})
        if settings.ENABLE_BREADCRUMBS:
            d['breadcrumbs'] = Breadcrumbs(self,min_length = settings.ENABLE_BREADCRUMBS)
        res = render_to_response(self.template_file, context_instance=context, **kwargs)
        self.content = res.content
        return self

    def add_pluginmedia(self, plugin):
        if plugin:
            p = self._plugincss.get(plugin.name, None)
            if p is None:
                css = plugin.css()
                if css:
                    self._plugincss[plugin.name] = css
                    
    def get_plugincss(self):
        css = ''.join(self._plugincss.values())
        if css:
            return Template(css).render(Context({'MEDIA_URL': settings.MEDIA_URL}))
        else:
            return ''
        