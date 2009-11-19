#
# Handle the view entry point

from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.conf import settings

from djpcms.settings import CONTENT_INLINE_EDITING
from djpcms.models import Page


__all__ = ['handler', 'get_view_from_page', 'get_view_from_url']



class reqcache(object):
    '''
    A cache object for a request.
    It avoids to create new view and hit the database for a page already requested
    during a HTTP request.
    It maintains a double dictionary of page ids and urls
    '''
    def __init__(self):
        self.urls  = {}
        self.pages = {}
        
    def add(self, view):
        self.urls[view.url] = view
        self.pages[view.page.id] = view 
        
    def url(self, url):
        return self.urls.get(url,None)
    
    def page(self, page):
        return self.pages.get(page.id,None)
    
    
def getcache(request):
    cache = getattr(request,'_djpcache',None)
    if cache is None:
        cache = reqcache()
        request._djpcache = cache
    return cache


def handler(request, url):
    '''
    Main entry for flatpage urls.
    request maintains a local cache for retriving
    pages already loaded
    '''
    # Create the page cache
    from djpcms.views.baseview import editview
    view, edit = _get_view_from_url(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    if edit:
        view = editview(view, edit)
    return view.response(request)

    
def get_view_from_url(request, url):
    '''
    wrap _get_view_from_url to return just the view
    This function is not called in editing mode
    '''
    view, edit = _get_view_from_url(request, url)
    return view
        

def get_view_from_page(request, page):
    '''
    Given a request and a page object it returns a view ovject
    '''
    cache = getcache(request)
    view  = cache.page(page)
    if view:
        return view
    
    if page.parent:
        view = get_view_from_page(request, page.parent)
        url  = '%s%s/' % (view.url, page.url_pattern)
    else:
        url = '/%s/' % page.url_pattern
    view = page.object(url = url)
    cache.add(view)
    return view
        

def _get_view_from_url(request, url):
    '''
    Get the page for the current request
    '''
    # First we check the url cache
    cache  = getcache(request)
    view   = cache.url(url)
    if view:
        return view, None
    
    url    = clean_url(url)
    if isinstance(url,HttpResponseRedirect):
        return set_page_cache(request, url)
    
    edit   = None
    parts  = None
    if url:
        parts  = url.split('/')
    
    # Check if we are editing
    # We are editing if the first part of the url is equal to
    # the preurl vale in the CONTENT_INLINE_EDITING dictionary
    if parts and CONTENT_INLINE_EDITING.get('available',False):
        editurl = CONTENT_INLINE_EDITING.get('preurl','edit')
        edit    = parts[0]
        if edit == editurl:
            parts.pop(0)
            url = u'/'.join(parts)
        else:
            edit = None

    page   = Page.objects.root()
    view   = page.object()
    cache.add(view)
    if parts:
        for part in parts:
            pages = page.children_pages.filter(url_pattern = part)
            if not pages:
                raise Http404('Flatpage %s not found' % request.path)
            else:
                page = pages[0]
            url   = u'%s%s/' % (view.url,part)
            view  = page.object(url = url)
            cache.add(view)
    
    redirect_page = page.redirect_to
    if redirect_page:
        return HttpResponseRedirect(redirect_page.get_absolute_url()), edit
    
    # Pages which requires login
    if page.requires_login and not request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_URL), edit

    return view, edit
    
    

def clean_url(path):
    url = path
    if url:
        modified = False
        if '//' in path:
            url = re.sub("/+" , "/", url)
            modified = True
    
        if not url.endswith('/'):
            modified = True
            url = '%s/' % url
            
        if modified:
            if not url.startswith('/'):
                url = '/%s' % url
            return HttpResponseRedirect(url)
    
        if url.endswith('/'):
            url = url[:-1]
        if url.startswith('/'):
            url = url[1:]
            
    return url