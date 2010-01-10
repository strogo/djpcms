from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django import http

from djpcms.utils.ajax import jsonbase

def saferender(f):
    
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            return mark_safe(force_unicode(e))
        
    return wrapper


def response_wrap(f):
    
    def wrapper(request, *args, **kwargs):
        res = f(request, *args, **kwargs)
        if isinstance(res, http.HttpResponse):
            return res
        elif isinstance(res,jsonbase):
            return http.HttpResponse(res.dumps(), mimetype='application/javascript')
        
    return wrapper