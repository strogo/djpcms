from django.conf import settings
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.utils.safestring import mark_safe

from djpcms.settings import HTML_CLASSES, POST_ERROR_TEMPLATE
from djpcms.html import TemplatePlugin, grid960
from djpcms.ajax import jhtmls
from djpcms.models import Page
from djpcms.skin import get_skin_style

from djpcms.extracontent import extra_content


class BlockListRender(object):
    
    def __init__(self, view, b):
        self.view = view
        self.blocks = view.page.blockcontent_set.filter(block = b+1)
    
    def __iter__(self):
        return self.blocks.__iter__()
    
    def __len__(self):
        return self.blocks.count()
    


class viewrequest(object):
    
    def __init__(self, view, request):
        self.view = view
        self.request = request


class djpcmsview(object):
    template_name = None
    
    def __unicode__(self):
        return u'%s' % self.url
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return str(self.__unicode__())
    
    def title(self):
        return ''
    
    def get_main_nav(self, request):
        return None
    
    def get_page_nav(self, request):
        return None
    
    def isfactory(self):
        return False
    
    def response(self, request):
        '''
        Entry point.
        NO NEED TO OVERRIDE THIS FUNCTION
        '''
        if request.method == 'GET':
            return self.get_view(request)
        else:
            return self.post_view(request)
        
    def get_template(self):
        return self.template_name or self.page.get_template()
        
    def get_view(self, request):
        '''
        Handle the Get view.
        This function SHOULD NOT be overwritten.
        Instead overwrite the view_contents method.
        '''
        template_name = self.get_template()
        if self.has_permission(request):
            # If user not authenticated set a test cookie  
            if not request.user.is_authenticated():
                request.session.set_test_cookie()
            
            pc = self.view_contents(request, request.GET)
            if isinstance(pc,HttpResponse):
                return pc
            
            try:
                sc = get_skin_style(self)
                if sc:
                    sc = mark_safe('<link rel="stylesheet" type="text/css" href="%s"/>' % sc)
            except:
                sc = None
        
            blocks = self.page.inner_template.numblocks()
            blockcontents = []
            for b in range(0,blocks):
                blockcontents.append(BlockListRender(self,b))
                
            c = {'cl':               self,
                 'root':             Page.objects.root(),
                 'sitenav':          self.get_main_nav(request),
                 'skin_style':       sc,
                 'grid':             self.grid960(),
                 'viewrequest':      viewrequest(self,request),
                 'contents':         blockcontents}
            extra_content(request,c,self)
        
            if isinstance(pc,dict):
                c.update(pc)
                    
        else:
            c = self.permission_denied()
        
        context_instance = RequestContext(request, c)
        return self.render_to_response(template_name    = template_name,  context_instance = context_instance)
    
    def grid960(self):
        return grid960()
        
    def view_contents(self, request, params):
        '''
        IMPORTANT METHOD
        By default just check if we need to redirect.
        This method is the one to override for implementing custom GET views.
        '''
        url = params.get('continue',None)
        if url:
            return self.redirect_to(url)
        return {}
    
    def post_view(self, request):
        '''
        Handle the post view
        '''
        post      = request.POST
        params    = dict(post.items())
        post_view = params.get(HTML_CLASSES.post_view_key, None)
        
        
        # If post_view key is defined, it means this is a AJAX-JSON request
        if post_view:
            post_view = post_view.replace('-','_').lower()

            try:
                try:
                    post_view_function  = getattr(self,str(post_view))
                except:
                    raise ValueError, 'Post view %s not available at %s' % (post_view,self)
                try:
                    res  = post_view_function(request, post)
                    return self.return_post(res)
                except Exception, e:
                    msg = "<p>Unhandled server error at %s in %s view: %s</p>" % (self, post_view, e)
                    raise ValueError, msg
            except Exception, e:
                return self.return_post(self.errorpost(e))
        
        # Standard post view (not AJAX-JSON)
        else:
            res = self.default_post(request, params)
            return self.return_post(res)
        
    def default_post(self, request, params):
        '''
        Default post view
        '''
        contin = params.get('continue',None)
        self.default_param_handling(params)
        return self.redirect_to(contin)
        
    def errorpost(self, msg):
        el = TemplatePlugin(template = POST_ERROR_TEMPLATE, inner = msg)
        return jhtmls(html = el.render(),
                      identifier = '.%s' % HTML_CLASSES.ajax_server_error)
        
    def return_post(self, res):
        '''
        Here it is assumed that res is an instance of
        djangosite.tools.ajax.rjson
        '''
        try:
            d = res.dumps()
            return HttpResponse(d, mimetype='application/javascript')
        except:
            return self.redirect_to()
        
    def redirect_to(self, url = None):
        if url == None:
            url = self.url
        return HttpResponseRedirect(url)
        
    def default_post(self, request, params):
        '''
        Default post view
        '''
        contin = params.get('continue',None)
        self.default_param_handling(params)
        return self.redirect_to(contin)
    
    def render_to_response(self, template_name = None, context_instance = None): 
        return render_to_response(template_name    = template_name,
                                  context_instance = context_instance)
        
    def default_param_handling(self, params):
        return None
    
    def has_permission(self, request):
        return True




class wrapview(djpcmsview):
    '''
    Create an object that wrap a view
    '''
    def __init__(self, view, prefix):
        self.page    = view.page
        self._view   = view
        self._prefix = prefix
        self.editurl = None
        self.url = '/%s%s' % (prefix,view.url)
        
    def get_template(self):
        return self.template_name or self._view.get_template()
    
    def view_contents(self, request, params):
        return self._view.view_contents(request, params)
    
    def grid960(self):
        return self._view.grid960()
    
    
class nopageview(djpcmsview):
    
    def __init__(self, baseurl):
        self.editurl = None
        self.url = baseurl