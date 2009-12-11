from djpcms.views.staticsite import handler
    
class StaticPagesMiddleware(object):
    '''
    Check For static Pages.
    If a static page is found return response object, otherwise return None
    '''
    def process_request(self, request):
        return handler(request)