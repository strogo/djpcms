from djpcms.views.site import handler

class LazyPage(object):
    def __get__(self, request, obj_type=None):
        get_page_from_request(request)
        return request._current_page_cache
    
    
class StaticPagesMiddleware(object):
    '''
    Check For static Pages.
    If a static page is found return response object, otherwise return None
    '''
    def process_request(self, request):
        url = request.path
        try:
            response = handler(request,url)
            return response
        except:
            return None