import re

from django.http import Http404, HttpResponseRedirect
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist

from djpcms.settings import CONTENT_INLINE_EDITING
from djpcms.models import Page
from djpcms.views import appsite


applications_url = appsite.site.urls



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
    try:
        page = Page.objects.get_flat_page(url)
        return page.object(),(),{}
    except ObjectDoesNotExist:
        resolver = urlresolvers.RegexURLResolver(r'^/', applications_url)
        try:
            return resolver.resolve(url)
        except:
            raise Http404


def Handler(request, url):
    view, args, kwargs = djpcmsHandler(request, url)
    if isinstance(view,HttpResponseRedirect):
        return view
    return view(request, *args, **kwargs).response()


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