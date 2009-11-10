
from djpcms.utils import function_module

def _no_extra_content(request,c,view):
    pass

def extra_content(request, c, view):
    from djpcms import settings
    func = function_module(settings.EXTRA_CONTENT_PLUGIN,_no_extra_content)
    return func(request,c,view)