import re

from django.http import Http404, HttpResponseRedirect

from djpcms.settings import CONTENT_INLINE_EDITING
from djpcms.views import appsite
from djpcms.views.cache import pagecache
from djpcms.views.response import DjpResponse
from djpcms.views.baseview import pageview 


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
    page = pagecache.get_from_url(url)
    if page:
        if page.application:
            view = appsite.site.getapp(page.application)
            if not view:
                raise Http404
            view.set_page(page)
        else:
            view = pageview(page)
        return view, (), {}
    else:
        applications_url = appsite.site.urls
        resolver = urlresolvers.RegexURLResolver(r'^/', applications_url)
        try:
            return resolver.resolve(url)
        except:
            raise Http404


def Handler(request, url):
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    view = view(request, *args, **kwargs)
    if isinstance(view,DjpResponse):
        return view.response()
    else:
        return view


def editHandler(request, url):
    '''
    Handle editing view
    '''
    from djpcms.views.baseview import editview
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    view = editview(view, CONTENT_INLINE_EDITING['preurl'])
    return view(request, *args, **kwargs).response()


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