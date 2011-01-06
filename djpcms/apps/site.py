import os
import sys
import logging

from djpcms.core.exceptions import AlreadyRegistered
from djpcms.utils.importer import import_module, import_modules
from djpcms.utils.collections import OrderedDict
from djpcms.core.urlresolvers import ResolverMixin


__all__ = ['MakeSite',
           'GetOrCreate',
           'get_site',
           'get_url',
           'get_urls',
           'loadapps',
           'sites']


class editHandler(ResolverMixin):
    
    def __init__(self, site):
        self.site = site
        
    def _load(self):
        return self.site.urls()
        


class ApplicationSites(ResolverMixin):
    
    def __init__(self):
        self.route = None
        self.sites = OrderedDict()
    
    def _load(self):
        '''Load sites'''
        from djpcms.apps.cache import PageCache
        self.pagecache = PageCache()
        settings = self.settings
        for site in self.sites.values():
            site.pagecache = self.pagecache
            site.load()
        import_modules(settings.DJPCMS_PLUGINS)
        import_modules(settings.DJPCMS_WRAPPERS)
        url = self.make_url
        urls = ()
        if settings.CONTENT_INLINE_EDITING['available']:
            edit = settings.CONTENT_INLINE_EDITING['preurl']
            for u,site in self.sites.items():
                urls += url(r'^{0}/{1}(.*)'.format(edit,u[1:]),
                            editHandler(site)),
        for u,site in self.sites.items():
            urls += url(r'^{0}(.*)'.format(u[1:]),
                        site),
        return urls
    
    def make(self, name, settings = None, route = None, clearlog = True):
        '''Initialise DjpCms from a directory or a file'''
        import djpcms
        #
        settings = settings or 'settings'
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
        
        if settings:
            sett = '{0}.py'.format(os.path.join(path,settings))
            if os.path.isfile(sett):
                os.environ['DJANGO_SETTINGS_MODULE'] = '{0}.{1}'.format(name,settings)
        
        # IMPORTANT! NEED TO IMPORT HERE TO PREVENT DJANGO TO IMPORT FIRST
        from djpcms.conf import settings
        settings.SITE_DIRECTORY = path
        settings.SITE_MODULE = name
        
        # IF no settings available get the current one
        if getattr(self,'settings',None) is None:
            self.settings = settings
        
        # Add template media directory to template directories
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        djpcms.init_logging(clearlog)
        self.logger = logging.getLogger('ApplicationSites')
        
        return self._create_site(route,settings)
    
    def _create_site(self,url,settings):
        from djpcms.apps import appsites
        url = self.makeurl(url)
        self.logger.info('Creating new site at route "{0}"'.format(url))
        site = self.get(url,None)
        if site:
            raise AlreadyRegistered('Site with url {0} already avalable "{1}"'.format(url,site))
        site = appsites.ApplicationSite(self.makeurl(url),settings)
        self.sites[site.route] = site
        self._urls = None
        return site
    
    def get(self, name, default = None):
        return self.sites.get(name,default)
    
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
        
    def clear(self):
        self.sites.clear()
        ResolverMixin.clear(self)
        
    def wsgi(self, environ, start_response):
        '''WSGI handler'''
        cleaned_path = self.clean_path(environ)
        if isinstance(cleaned_path,self.http.HttpResponseRedirect):
            return cleaned_path
        path = cleaned_path[1:]
        site,view,kwargs = self.resolve(path)
        request = site.http.Request(environ)
        request.site = site
        djp = view(request, **kwargs)
        return djp.response()
    
    def request_handler(self, request, url):
        '''Entry points for requests'''
        cleaned_path = self.clean_path(request.environ)
        if isinstance(cleaned_path,self.http.HttpResponseRedirect):
            return cleaned_path
        path = cleaned_path[1:]
        site,view,kwargs = self.resolve(path)
        request.site = site
        djp = view(request, **kwargs)
        setattr(request,'instance',djp.instance)
        return djp.response()
        
        
        
sites = ApplicationSites()

MakeSite = sites.make
GetOrCreate = sites.get_or_create
get_site = sites.get_site
get_url  = sites.get_url
get_urls = sites.get_urls
loadapps = sites.load

