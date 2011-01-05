from werkzeug import wrappers
from werkzeug import exceptions

Request = wrappers.Request
HTTPResponse = wrappers.Response

HTTPException = exceptions.HTTPException
Http404 = exceptions.NotFound


class make_wsgi(object):
    
    def __init__(self, app):
        local.application = app
        
    def __call__(self, environ, start_response):
        request = Request(environ)
        Handler(request, url):
    '''Entry points for requests'''
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    djp = view(request, **kwargs)
    if isinstance(djp,DjpResponse):
        setattr(request,'instance',djp.instance)
        return djp.response()
    else:
        setattr(request,'instance',None)
        return djp
        try:
            endpoint, values = app.match()


