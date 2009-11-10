from djpcms.views.site import get_page_from_request

class LazyPage(object):
    def __get__(self, request, obj_type=None):
        get_page_from_request(request)
        return request._current_page_cache
    
    
class CurrentPageMiddleware(object):
    
    def process_request(self, request):
        request.__class__._pagecache = {}
        request.__class__.current_page = LazyPage()
        return None
