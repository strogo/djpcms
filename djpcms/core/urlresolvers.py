#
# MODULE ADAPTED FROM DJANGO
#
# Original file in django.core.urlresolvers
#
#
#

"""
This module converts requested URLs to callback view functions.

RegexURLResolver is the main class here. Its resolve() method takes a URL (as
a string) and returns a tuple in this format:

    (view_function, function_args, function_kwargs)
"""

import re
from inspect import isclass

from djpcms.core.exceptions import ImproperlyConfigured, ViewDoesNotExist
from djpcms.http import get_http
from django.utils.datastructures import MultiValueDict
from django.utils.encoding import iri_to_uri, force_unicode, smart_str
from django.utils.functional import memoize
from django.utils.regex_helper import normalize

_view_cache = {}

class Resolver404(Exception):
    pass


class ResolverMixin(object):
    
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
    
    def clear(self):
        global _view_cache
        self.resolver = None
        self._urls = None
        _view_cache.clear()
    
    def clean_path(self, environ):
        '''
        Clean url and redirect if needed
        '''
        path = environ['PATH_INFO']
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
    
    def resolve(self, path, subpath = None, site = None):
        global _view_cache
        subpath = subpath if subpath is not None else path
        cached = _view_cache.get(path,None)
        if not cached:
            if not getattr(self,'resolver',None):
                urls = self.urls()
                self.resolver = RegexURLResolver(r'^', urls)
            
            if not site:
                view = self.resolve_flat(path)
                if view:
                    res = (self,view,{})
                    _view_cache[path] = res
                    return res
            try:
                view, rurl, kwargs = self.resolver.resolve(subpath)
            except Resolver404 as e:
                raise self.http.Http404(str(e))
            if isinstance(view,ResolverMixin):
                if len(rurl) == 1:
                    return view.resolve(path, rurl[0], site or view)
                else:
                    raise self.http.Http404
            else:
                res = (site,view,kwargs)
                _view_cache[path] = res
                return res
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
                        sub_match_dict = dict([(smart_str(k), v) for k, v in match.groupdict().items()])
                        sub_match_dict.update(self.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[smart_str(k)] = v
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

    def reverse(self, lookup_view, *args, **kwargs):
        if args and kwargs:
            raise ValueError("Don't mix *args and **kwargs in call to reverse()!")
        try:
            lookup_view = get_callable(lookup_view, True)
        except (ImportError, AttributeError), e:
            raise NoReverseMatch("Error importing '%s': %s." % (lookup_view, e))
        possibilities = self.reverse_dict.getlist(lookup_view)
        for possibility, pattern in possibilities:
            for result, params in possibility:
                if args:
                    if len(args) != len(params):
                        continue
                    unicode_args = [force_unicode(val) for val in args]
                    candidate =  result % dict(zip(params, unicode_args))
                else:
                    if set(kwargs.keys()) != set(params):
                        continue
                    unicode_kwargs = dict([(k, force_unicode(v)) for (k, v) in kwargs.items()])
                    candidate = result % unicode_kwargs
                if re.search(u'^%s' % pattern, candidate, re.UNICODE):
                    return candidate
        # lookup_view can be URL label, or dotted path, or callable, Any of
        # these can be passed in at the top, but callables are not friendly in
        # error messages.
        m = getattr(lookup_view, '__module__', None)
        n = getattr(lookup_view, '__name__', None)
        if m is not None and n is not None:
            lookup_view_s = "%s.%s" % (m, n)
        else:
            lookup_view_s = lookup_view
        raise NoReverseMatch("Reverse for '%s' with arguments '%s' and keyword "
                "arguments '%s' not found." % (lookup_view_s, args, kwargs))


def clear_url_caches():
    global _resolver_cache
    global _callable_cache
    _resolver_cache.clear()
    _callable_cache.clear()

