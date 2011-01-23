#
# MODULE ADAPTED FROM DJANGO
#
# Original file in django.core.urlresolvers
#
#
#

import re
from inspect import isclass

from djpcms.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from djpcms.http import get_http
from djpcms.utils import force_str

_view_cache = {}


class Resolver404(Exception):
    pass

    
def cachevalue(path, view, site, editsite, kwargs):
    '''add a path in the cache dictionary. The value is composed by
    
    (site,view,kwargs)
    
The parameters are:

:parameter path: absolute path to view (excluding leading slash).
:parameter view: instance of :class:`djpcms.views.baseview.djpcmsview`.
:parameter site: instance of the application site containing the ``view``
:parameter editsite: a site instance or None. If defined this is an ediding view.
:parameter kwargs: dictionary of view parameters.'''
    from djpcms.views.baseview import editview
    if editsite:
        site = editsite
        view = editview(view, site.settings.CONTENT_INLINE_EDITING['preurl'])
    cached = (site,view,kwargs)
    _view_cache[path] = cached
    return cached


class ResolverMixin(object):
    '''A lazy mixin class for resolving urls. The main function here is the ``resolve``
method'''
    
    def load(self):
        if getattr(self,'_urls',None) is None:
            self._urls = self._load()
        
    def __get_isloaded(self):
        return getattr(self,'_urls',None) is not None
    isloaded = property(__get_isloaded)
    
    def urls(self):
        self.load()
        return self._urls
    
    def _load(self):
        pass
    
    def editsite(self):
        return False
    
    def clearcache(self):
        global _view_cache
        self.resolver = None
        self._urls = None
        _view_cache.clear()
        pagecache = getattr(self,'pagecache',None)
        if pagecache:
            pagecache.clear()
        
    def clear(self):
        self.clearcache()
    
    def clean_path(self, environ):
        '''Clean url and redirect if needed
        '''
        path = environ['PATH_INFO']
        url = path
        if url:
            modified = False
            if '//' in path:
                url = re.sub("/+" , "/", url)
                modified = True
        
            #if not url.endswith('/'):
            #    modified = True
            #    url = '%s/' % url
                
            if modified:
                if not url.startswith('/'):
                    url = '/%s' % url
                qs = environ['QUERY_STRING']
                if qs and environ['method'] == 'GET':
                    url = '{0}?{1}'.format(url,qs)
                return self.http.HttpResponseRedirect(url)
        return url

    def __get_http(self):
        return get_http(self.settings.HTTP_LIBRARY)
    http = property(__get_http, "Return the http library handle")
    
    def make_url(self, regex, view, kwargs=None, name=None):
        return RegexURLPattern(regex, view, kwargs, name)
    
    def resolve(self, path, subpath = None, site = None, editsite = False):
        global _view_cache
        subpath = subpath if subpath is not None else path
        cached = _view_cache.get(path,None)
        if not cached:
            if not getattr(self,'resolver',None):
                urls = self.urls()
                self.resolver = RegexURLResolver(r'^', urls)
            
            if not site:
                view = self.resolve_flat(subpath)
                if view:
                    try:
                        site = self.get_site()
                    except:
                        site = self
                    return cachevalue(path, view, site, editsite, {})
            try:
                view, rurl, kwargs = self.resolver.resolve(subpath)
            except Resolver404 as e:
                raise self.http.Http404(str(e))
            if isinstance(view,ResolverMixin):
                if len(rurl) == 1:
                    edit = view.editsite()
                    if edit:
                        return view.resolve(path, rurl[0], None, edit)
                    else:
                        return view.resolve(path, rurl[0], site or view, editsite)
                else:
                    raise self.http.Http404
            else:
                return cachevalue(path, view, site, editsite, kwargs)
        else:
            return cached
        
    def resolve_flat(self, path):
        '''Resolve flat pages'''
        from djpcms.models import Page
        from djpcms.views.baseview import pageview
        try:
            page = Page.objects.sitepage(url = '/'+path)
        except:
            return None
        if not page.application_view:
            return pageview(page)

    

class RegexURLPattern(object):
    """ORIGINAL CLASS FROM DJANGO    www.djangoproject.com

Adapted for djpcms
"""
    def __init__(self, regex, callback,
                 default_args=None,
                 name=None):
        # regex is a string representing a regular expression.
        # callback is either a string like 'foo.views.news.stories.story_detail'
        # which represents the path to a module and a view function name, or a
        # callable object (view).
        self.regex = re.compile(regex, re.UNICODE)
        self.callback = callback
        self.default_args = default_args or {}
        self.name = name

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.name, self.regex.pattern)

    def resolve(self, path):
        match = self.regex.search(path)
        if match:
            # If there are any named groups, use those as kwargs, ignoring
            # non-named groups. Otherwise, pass all non-named arguments as
            # positional arguments.
            kwargs = match.groupdict()
            if kwargs:
                args = ()
            else:
                args = match.groups()
            # In both cases, pass any extra_kwargs as **kwargs.
            kwargs.update(self.default_args)

            return self.callback, args, kwargs


class RegexURLResolver(object):
    """This class ``resolve`` method takes a URL (as
a string) and returns a tuple in this format:

    (view_function, function_args, function_kwargs)
    
ORIGINAL CLASS FROM DJANGO    www.djangoproject.com

Adapted for djpcms
"""
    def __init__(self, regex, urlconf_name, default_kwargs=None, app_name=None, namespace=None):
        # regex is a string representing a regular expression.
        # urlconf_name is a string representing the module containing URLconfs.
        self.regex = re.compile(regex, re.UNICODE)
        self.urlconf_name = urlconf_name
        if not isinstance(urlconf_name, basestring):
            self._urlconf_module = self.urlconf_name
        self.callback = None
        self.default_kwargs = default_kwargs or {}
        self.namespace = namespace
        self.app_name = app_name
        self._reverse_dict = None
        self._namespace_dict = None
        self._app_dict = None

    def __repr__(self):
        return '<%s %s (%s:%s) %s>' % (self.__class__.__name__, self.urlconf_name, self.app_name, self.namespace, self.regex.pattern)

    def _get_app_dict(self):
        if self._app_dict is None:
            self._populate()
        return self._app_dict
    app_dict = property(_get_app_dict)

    def resolve(self, path):
        tried = []
        match = self.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in self.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([(pattern.regex.pattern + '   ' + t) for t in sub_tried])
                    else:
                        tried.append(pattern.regex.pattern)
                else:
                    if sub_match:
                        sub_match_dict = dict([(force_str(k), v) for k, v in match.groupdict().items()])
                        sub_match_dict.update(self.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[force_str(k)] = v
                        return sub_match[0], sub_match[1], sub_match_dict
                    tried.append(pattern.regex.pattern)
            raise Resolver404({'tried': tried, 'path': new_path})
        raise Resolver404({'path' : path})

    def _get_urlconf_module(self):
        try:
            return self._urlconf_module
        except AttributeError:
            self._urlconf_module = import_module(self.urlconf_name)
            return self._urlconf_module
    urlconf_module = property(_get_urlconf_module)

    def _get_url_patterns(self):
        patterns = getattr(self.urlconf_module, "urlpatterns", self.urlconf_module)
        try:
            iter(patterns)
        except TypeError:
            raise ImproperlyConfigured("The included urlconf %s doesn't have any patterns in it" % self.urlconf_name)
        return patterns
    url_patterns = property(_get_url_patterns)

    def _resolve_special(self, view_type):
        callback = getattr(self.urlconf_module, 'handler%s' % view_type)
        try:
            return get_callable(callback), {}
        except (ImportError, AttributeError), e:
            raise ViewDoesNotExist("Tried %s. Error was: %s" % (callback, str(e)))

    def resolve404(self):
        return self._resolve_special('404')

    def resolve500(self):
        return self._resolve_special('500')



