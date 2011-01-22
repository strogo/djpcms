from werkzeug import wrappers
from werkzeug import exceptions
from werkzeug.serving import run_simple


from djpcms import sites


Request = wrappers.Request
HttpResponse = wrappers.Response


def make_request(environ):
    request = Request(environ)
    request.COOKIES = request.cookies
    return request
    

def finish_response(response, environ, start_response):
    return response(environ, start_response)


def HttpResponseRedirect(location):
    r = HttpResponse(status = 301)
    r.location = location
    return r
        

HTTPException = exceptions.HTTPException
Http404 = exceptions.NotFound



def is_authenticated(request):
    return request.user.is_authenticated()



def serve(port = 8060, use_reloader = False):
    run_simple('localhost',port,sites.wsgi,use_reloader)