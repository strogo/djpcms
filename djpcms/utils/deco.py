from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode

def saferender(f):
    
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            return mark_safe(force_unicode(e))
        
    return wrapper