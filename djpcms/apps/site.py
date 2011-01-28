import os
import sys
import copy
import logging

import djpcms
from djpcms.conf import get_settings
from djpcms.core.exceptions import AlreadyRegistered, PermissionDenied,\
                                   ImproperlyConfigured
from djpcms.utils.importer import import_module, import_modules
from djpcms.utils import logerror
from djpcms.utils.collections import OrderedDict
from djpcms.core.urlresolvers import ResolverMixin


__all__ = ['MakeSite',
           'GetOrCreate',
           'get_site',
           'get_url',
           'get_urls',
           'loadapps',
           'sites']


logger = logging.getLogger('sites')


class editHandler(ResolverMixin):
    
    def __init__(self, site):
        self.site = site
        self.settings = site.settings
        
    def _load(self):
        return self.site.urls()
    
    def editsite(self):
        return self.site
        


class ApplicationSites(ResolverMixin):
    '''This class is used as a singletone and holds information
of djpcms routes'''
    
    def __init__(self):
        self._sites = {}
        self.modelwrappers = {}
        self.clear()
        
    def clear(self):
        self._sites.clear()
        self._osites = None
        self._settings = None
        self._default_settings = None
        self.route = None
        self.model_from_hash = {}
        self.User = None
        ResolverMixin.clear(self)
        for wrapper in self.modelwrappers.values():
            wrapper.clear()
        
    def register_orm(self, name):
        '''Register a new Object Relational Mapper to Djpcms. ``name`` is the
    dotted path to a python module containing a class named ``OrmWrapper``
    derived from :class:`BaseOrmWrapper`.'''
        names = name.split('.')
        if len(names) == 1:
            mod_name = 'djpcms.core.orms._' + name
        else:
            mod_name = name
        try:
            mod = import_module(mod_name)
        except ImportError:
            return
        self.modelwrappers[name] = mod.OrmWrapper
        
    def __len__(self):
        return len(self._sites)
    
    def all(self):
        s = self._osites
        if s is None:
            self._osites = s = OrderedDict(reversed(sorted(self._sites.items(),
                                           key=lambda x : x[0]))).values()
        return s                           
                                           
    def __iter__(self):
        return self.all().__iter__()
    
    def __getitem__(self, index):
        return self.all()[index]
    def __setitem(self, index, val):
        raise TypeError('Site object does not support item assignment')
        
    def __get_settings(self):
        if not self._settings:
            if not self._default_settings:
                self._default_settings = get_settings()
            return self._default_settings
        else:
            return self._settings
    settings = property(__get_settings)
    
    def setup_environment(self):
        for wrapper in self.modelwrappers.values():
            wrapper.setup_environment()
        
    def _load(self):
        '''Load sites'''
        #from djpcms.apps.cache import PageCache
        #self.pagecache = PageCache()
        if not self._sites:
            raise ImproperlyConfigured('No sites registered.')
        self.setup_environment()
        settings = self.settings
        sites = self.all()
        for site in sites:
            site.load()
        import_modules(settings.DJPCMS_PLUGINS)
        import_modules(settings.DJPCMS_WRAPPERS)
        url = self.make_url
        urls = ()
        if settings.CONTENT_INLINE_EDITING['available']:
            edit = settings.CONTENT_INLINE_EDITING['preurl']
            for site in sites:
                urls += url(r'^{0}/{1}(.*)'.format(edit,site.route[1:]),
                            editHandler(site)),
        for site in sites:
            urls += url(r'^{0}(.*)'.format(site.route[1:]),
                        site),
        return urls
    
    def make(self, name, settings = None, route = None, clearlog = True, **kwargs):
        '''Create a new DjpCms site from a directory or a file'''
        # if not a directory it may be a file
        if os.path.isdir(name):
            appdir = name
        elif os.path.isfile(name):
            appdir = os.path.split(os.path.realpath(name))[0]
        else:
            try:
                mod = import_module(name)
                appdir = mod.__path__[0]
            except ImportError:
                raise ValueError('Could not find directory or file {0}'.format(name))
        path = os.path.realpath(appdir)
        base,name = os.path.split(path)
        if base not in sys.path:
            sys.path.insert(0, base)
        
        # Import settings
        settings = settings or 'settings'
        if '.' in settings:
            settings_module_name = settings
        else:
            sett = '{0}.py'.format(os.path.join(path,settings))
            if os.path.isfile(sett):
                settings_module_name = '{0}.{1}'.format(name,settings)
            else:
                settings_module_name = None
        
        # IMPORTANT! NEED TO IMPORT HERE TO PREVENT DJANGO TO IMPORT FIRST
        settings = get_settings(settings_module_name,
                                SITE_DIRECTORY = path,
                                SITE_MODULE = name,
                                **kwargs)
        
        # If no settings available get the current one
        if self._settings is None:
            self._settings = settings
            sk = getattr(settings,'SECRET_KEY',None)
            if not sk:
                settings.SECRET_KEY = 'djpcms'
            djpcms.init_logging(clearlog)
        
        # Add template media directory to template directories
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        self.logger = logging.getLogger('ApplicationSites')
        
        return self._create_site(route,settings)
    
    def _create_site(self,url,settings):
        from djpcms.apps import appsites
        url = self.makeurl(url)
        self.logger.info('Creating new site at route "{0}"'.format(url))
        site = self.get(url,None)
        if site:
            raise AlreadyRegistered('Site with url {0} already avalable "{1}"'.format(url,site))
        site = appsites.ApplicationSite(self, url, settings)
        self._sites[site.route] = site
        self._osites = None
        self._urls = None
        return site
    
    def get(self, name, default = None):
        return self._sites.get(name,default)
    
    def get_or_create(self, name, settings = None, route = None):
        route = self.makeurl(route)
        site = self.get(route,None)
        if site:
            return site
        else:
            return self.make(name,settings,route)
    
    def makeurl(self, url = None):
        url = url or '/'
        if not url.endswith('/'):
            url += '/'
        if not url.startswith('/'):
            url = '/' + url
        return url
            
    def get_site(self, url = None):
        url = self.makeurl(url)
        site = self.get(url,None)
        if not site:
            try:
                res = self.resolve(url[1:])
                return res[0]
            except:
                return None
        else:
            return site
        
    def get_urls(self):
        urls = []
        for site in self.values():
            urls.extend(site.get_urls())
        return urls
     
    def get_url(self, model, view_name, instance = None, url = None, **kwargs):
        site = self.get_site(url)
        if not site:
            return None
        return site.get_url(model, view_name, instance = None, **kwargs)
        if not isinstance(model,type):
            instance = model
            model = instance.__class__
        app = site.for_model(model)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
    
    def view_from_page(self, page):
        site = self.get_site(page.url)
        
    def wsgi(self, environ, start_response):
        '''DJPCMS WSGI handler'''
        http = self.http
        HttpResponse = http.HttpResponse
        response = None
        site = None
        try:
            cleaned_path = self.clean_path(environ)
            if isinstance(cleaned_path,HttpResponse):
                return http.finish_response(cleaned_path, environ, start_response)
            path = cleaned_path[1:]
            request = http.make_request(environ)
            request.site = self
            site,view,kwargs = self.resolve(path)
            request.site = site
            djp = view(request, **kwargs)
            if not isinstance(djp,HttpResponse):
                request.data_dict = dict(request.args.items())
                #signals.request_started.send(sender=self.__class__)
                # Request middleware
                for middleware_method in site.request_middleware():
                    response = middleware_method(request)
                    if response:
                        return http.finish_response(response, environ, start_response)
                response = djp.response()
                # Response middleware
                for middleware_method in site.response_middleware():
                    middleware_method(request,response)
            else:
                response = djp
        except PermissionDenied:
            response = http.HttpResponse(status = 403)
        except http.Http404 as e:
            response = http.HttpResponse(status = 404)
        except Exception as e:
            logerror(logger, request, sys.exc_info())
            if site:
                for middleware_method in site.exception_middleware():
                    response = middleware_method(request, e)
                    if response:
                        break
            if not response:
                response = http.HttpResponse(status = 500)
        return http.finish_response(response, environ, start_response)
    
    def djp(self, request, path):
        '''Entry points for requests'''
        site,view,kwargs = self.resolve(path)
        request.site = site
        djp = view(request, **kwargs)
        setattr(request,'instance',djp.instance)
        return djp
        
    def request_handler(self, request, url):
        '''Entry points for requests'''
        cleaned_path = self.clean_path(request.environ)
        if isinstance(cleaned_path,self.http.HttpResponse):
            return cleaned_path
        try:
            djp = self.djp(request,url)
            if isinstance(djp,self.http.HttpResponse):
                return djp
            else:
                return djp.response()
        except PermissionDenied as e:
            settings = request.site.settings
            if settings.HTTP_LIBRARY == 'django':
                from django.core import exceptions
                raise exceptions.PermissionDenied(e)
            else:
                raise           
        
        
        
sites = ApplicationSites()

MakeSite = sites.make
GetOrCreate = sites.get_or_create
get_site = sites.get_site
get_url  = sites.get_url
get_urls = sites.get_urls
loadapps = sites.load

