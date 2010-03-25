from djpcms.utils.navigation import Navigator
from djpcms.views.cache import pagecache
from djpcms.utils.html import grid960
from djpcms.conf import settings


# Aijack admin site to inject some specific djpcms stuff

def _add_to_context(request, context):
    try:
        view = pagecache.view_from_url(request, '/')
        nav  = Navigator(view(request))
    except:
        nav = None
    context = context or {}
    context.update({'admin_site': True,
                    'cssajax': settings.HTML_CLASSES,
                    'grid':    grid960(),
                    'sitenav': nav})
    return context