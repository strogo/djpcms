'''
view cache.
This module handle the creation and caching of new view objects
'''
from django.http import Http404
from django.db.models.signals import post_save

from djpcms.models import Page
from djpcms.settings import CACHE_VIEW_OBJECTS


def get(url):
    if url:
        url = '/%s/' % url
    else:
        url = '/'
    return _cache.get(url,None)


def handle_new_view(page, args, **kwargs):
    '''
    Create a new view object
    '''
    view = page.object(args, **kwargs)
    register_cache(view)
    
    # Check Factory options.
    if view.isfactory():
        if not hasattr(view,'default_handler'):
            default_handler = handle_new_view_from_view(view, [view.default_view])
            view.set_default_handler(default_handler)
        if not args:
            return view
        else:
            while args:
                view = handle_new_view_from_view(view, args)
    
    if args:
        raise Http404
    
    return view


def handle_new_view_from_view(view, args):
    nview = view.get_child(args)
    register_cache(nview)
    return nview



################################################################
###    PUBLIC API

def view_from_page(page, args = None, **kwargs):
    if not page:
        return None
    if page.parent:
        url = page.modified_url_pattern()
    else:
        url = '/'
    args = args or []
    if args:
        try:
            url = url % tuple(args)
            args = None
        except:
            pass
    try:
        view = _cache[url]
        if args:
            return handle_new_view_from_view(view,args)
        else:
            return view
    except:
        return handle_new_view(page, args, **kwargs)



def get_page_view(code = None, args = None, **kwargs):
    if code:
        page = Page.objects.get_for_code(code)
    else:
        page = Page.objects.root()
    return view_from_page(page, args, **kwargs)


def childview(request, view, args):
    url = '%s%s/' % (view,'/'.join(args))
    try:
        view = _cache[url]
    except:
        view = handle_new_view_from_view(view, args)
        
    if view and view.has_permission(request):
        return view
    else:
        return None
    

#######################################################################
##
##        CACHE HANDLING

def register_cache(view):
    '''
    Here we add view object to the cache.
    if a view has an object, the view is removed from the cache when the object is saved 
    '''
    #TODO cascaed to view children as well
    global _cache
    global _cache_model
    if not CACHE_VIEW_OBJECTS:
        return
    if view and view.incache():
        if not _cache.has_key(view.url):
            _cache[view.url] = view
            object = view.object
            if object:
                cm = cachemodel(view.model)
                cma = _cache_model.get(cm.name(), None)
                if not cma:
                    cma = cm
                    _cache_model[cm.name()] = cma
                    cma.register()
                    
                    
class cachemodel(object):
    
    def __init__(self, model):
        self.model = model
    
    def name(self):
        return str(self.model._meta)
    
    def register(self):
        post_save.connect(self._clear_cache, sender=self.model)
        
    def _clear_cache(self, sender, **kwargs):
        global _cache
        newcache = {}
        for k,view in _cache.items():
            if not isinstance(view.object, self.model):
                newcache[k] = view
        _cache = newcache
        

def newcache(sender, **kwargs):
    global _cache
    _cache = {}

post_save.connect(newcache, sender=Page)


_cache = {}
_cache_model = {}