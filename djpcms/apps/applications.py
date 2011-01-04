import os
import sys
import logging

from djpcms.core.exceptions import AlreadyRegistered
from djpcms.utils.collections import OrderedDict
from djpcms.core.urlresolvers import SiteResolver


__all__ = ['MakeSite',
           'GetOrCreate',
           'get_site',
           'get_url',
           'get_urls',
           'loadapps',
           'sites']


class ApplicationSites(OrderedDict,SiteResolver):
    
    def import_module(self, name):
        from django.utils.importlib import import_module
        return import_module(name)
    
    def load(self):
        for site in self.values():
            if not site.isloaded:
                name = site.settings.APPLICATION_URL_MODULE
                if name:
                    app_module = self.import_module(name)
                    appurls = app_module.appurls
                else:
                    appurls = ()
                site.load(*appurls)
            
    def make(self, name, settings = None, url = None, clearlog = True):
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
                mod = self.import_module(name)
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
        
        # Add template media directory to template directories
        path = os.path.join(djpcms.__path__[0],'media','djpcms')
        if path not in settings.TEMPLATE_DIRS:
            settings.TEMPLATE_DIRS += path,
        
        djpcms.init_logging(clearlog)
        self.logger = logging.getLogger('ApplicationSites')
        
        return self._create_site(url,settings)
    
    def _create_site(self,url,settings):
        from djpcms.apps import appsites
        url = self.makeurl(url)
        self.logger.info('Creating new site at route "{0}"'.format(url))
        site = self.get_site(url)
        if site:
            raise AlreadyRegistered('Site with url {0} already avalable "{1}"'.format(url,site))
        site = appsites.ApplicationSite(self.makeurl(url),settings)
        self[site.url] = site
        self._urls = None
        return site
    
    def get_or_create(self, name, settings = None, route = None):
        route = self.makeurl(route)
        site = self.get_site(route)
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
                return self.resolve(url)
            except:
                return None
        else:
            return site

    def urls(self):
        urls = getattr(self,'_urls',None)
        if urls is None:
            from django.conf.urls.defaults import url
            urls = ()
            for u,site in self.items():
                urls += url(r'^{0}(.*)'.format(u[1:]), site),
            self._urls = urls
        return urls
        
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
        self._urls = None
        OrderedDict.clear(self)


sites = ApplicationSites()

MakeSite = sites.make
GetOrCreate = sites.get_or_create
get_site = sites.get_site
get_url  = sites.get_url
get_urls = sites.get_urls
loadapps = sites.load
