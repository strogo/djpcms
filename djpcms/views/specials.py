from django import http

from djpcms.views.baseview import djpcmsview

class badview(djpcmsview):
    
    def __init__(self, template, httphandler):
        self.template = template
        self.httphandler = httphandler
        super(badview,self).__init__(*args, **kwargs)
        
    def response(self, request):
        return self.handler()

def http404view(request, *args, **kwargs):
    return badview('exceptions/404.html',http.HttpResponseNotFound).response(request)

def http500view(request, *args, **kwargs):
    return badview('exceptions/500.html',http.HttpResponseServerError).response(request)