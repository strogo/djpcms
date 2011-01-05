from djpcms import sites
from djpcms.http import get_http
from djpcms.template import RequestContext, loader
from djpcms.views.baseview import djpcmsview


class badview(djpcmsview):
    
    def __init__(self, template, httphandler):
        self.template = template
        self.httphandler = httphandler
        super(badview,self).__init__()
        
    def response(self, request):
        t = loader.get_template(self.template)
        c = {'request_path': request.path,
             'grid': self.grid960()}
        return self.httphandler(t.render(RequestContext(request, c)))

def http404view(request, *args, **kwargs):
    http = get_http(sites.settings.HTTP_LIBRARY)
    return badview('404.html',
                   http.HttpResponseNotFound).response(request)

def http500view(request, *args, **kwargs):
    http = get_http(sites.settings.HTTP_LIBRARY)
    return badview('500.html',
                   http.HttpResponseServerError).response(request)