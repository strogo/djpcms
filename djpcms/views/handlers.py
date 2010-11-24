import re

from django.http import Http404, HttpResponseRedirect

from djpcms.conf import settings
from djpcms.views import appsite
from djpcms.views.cache import pagecache
from djpcms.views.response import DjpResponse 


def djpcmsHandler(request, url):
    '''
    Fetch a static view or an application view
    '''
    from django.core import urlresolvers
    
    #url = clean_url('/{0}'.format(url))    Python 3.1
    url = clean_url('/%s' % url)
    if isinstance(url,HttpResponseRedirect):
        return url, (), {}
    
    # First we check for static pages
    if not request.is_ajax():
        view = pagecache.view_from_url(request, url)
        if view and not view.names():
            return view, (), {}

    resolver = urlresolvers.RegexURLResolver(r'^/', pagecache.build_app_urls(request))
    try:
        apphandler, args, kwargs = resolver.resolve(url)
        return apphandler(request, *args, **kwargs) 
    except Exception, e:
        raise Http404


def response(request, url):
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    return view(request, **kwargs)
    

def Handler(request, url):
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


def editHandler(request, url):
    '''
    Handle editing view
    '''
    from djpcms.views.baseview import editview
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    view = editview(view, settings.CONTENT_INLINE_EDITING['preurl'])
    return view(request, **kwargs).response()


def clean_url(path):
    '''
    Clean url and redirect if needed
    '''
    url = path
    if url:
        modified = False
        if '//' in path:
            url = re.sub("/+" , "/", url)
            modified = True
    
        if not url.endswith('/'):
            modified = True
            url = '%s/' % url
            
        if modified:
            if not url.startswith('/'):
                url = '/%s' % url
            return HttpResponseRedirect(url)
    
        #if url.endswith('/'):
        #    url = url[:-1]
        #if url.startswith('/'):
        #    url = url[1:]
            
    return url

