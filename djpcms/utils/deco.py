from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django import http

from djpcms.utils.ajax import jsonbase, jservererror

def saferender(f):
    
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            return mark_safe(force_unicode(e))
        
    return wrapper


def response_wrap(f):
    
    def wrapper(request, *args, **kwargs):
        from django.conf import settings
        ajax = request.is_ajax()
        try:
            res = f(request, *args, **kwargs)
        except Exception, e:
            # we got an error. If in debug mode send a JSON response with
            # the error message back to javascript.
            if settings.DEBUG and ajax:
                res = jservererror(e, url = request.path)
            else:
                raise e
            
        if isinstance(res, http.HttpResponse):
            return res
        elif isinstance(res,jsonbase) and ajax:
            return http.HttpResponse(res.dumps(), mimetype='application/javascript')
        else:
            return res
        
    return wrapper