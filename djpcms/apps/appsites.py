from threading import Lock

from djpcms.core.exceptions import DjpcmsException, AlreadyRegistered,\
                                   ImproperlyConfigured, ApplicationNotAvailable
from djpcms.views.appsite import Application, ModelApplication
from djpcms.utils.collections import OrderedDict
from djpcms.utils.importer import import_module, module_attribute
from djpcms.core.urlresolvers import ResolverMixin
from djpcms.http import make_wsgi

from djpcms.models import BlockContent
from djpcms.apps.included.contentedit import ContentSite



class ApplicationSite(ResolverMixin):
    '''
    Application site manager
    An instance of this class is used to handle url of
    registered applications.
    '''
    def __init__(self, root, url, config):
        self.lock = Lock()
        self.root = root
        self.route = url
        self.url = url
        self.config = config
        self.settings = config
        self.editavailable = config.CONTENT_INLINE_EDITING.get('available',False)
        self.editurl  = config.CONTENT_INLINE_EDITING.get('preurl','/edit/')
        self._registry = {}
        self._nameregistry = OrderedDict()
        self.choices = [('','-----------------')]
        self._request_middleware = None
        self._response_middleware = None
        self.ModelApplication = ModelApplication
        
    def __repr__(self):
        return '{0} - {1}'.format(self.route,'loaded' if self.isloaded else 'not loaded')
    __str__ = __repr__
    
    def __get_User(self):
        return self.root.User
    def __set_User(self, User):
        if not self.root.User:
            self.root.User = User
        elif User is not self.root.User:
            raise ImproperlyConfigured('A different User class has been already registered')
    User = property(__get_User,__set_User)
    
    def load_initial(self):
        baseurl = self.config.CONTENT_INLINE_EDITING.get('pagecontent', '/content/')
        self.register(ContentSite(baseurl, BlockContent, editavailable = False))
        
    def count(self):
        return len(self._registry)
        
    def _load(self):
        """Registers an instance of :class:`djpcms.views.appsite.Application`
to the site. If a model is already registered, this will raise AlreadyRegistered."""
        name = self.settings.APPLICATION_URL_MODULE
        appurls = ()
        if name:
            app_module = import_module(name)
            appurls = app_module.appurls
            if hasattr(appurls,'__call__'):
                appurls = appurls()
        self.load_initial()
        for application in appurls:
            self.register(application)
        url = self.make_url
        urls = ()
        # Add in each model's views.
        for app in self._nameregistry.values():
            baseurl = app.baseurl
            if baseurl:
                urls += url('^{0}(.*)'.format(baseurl[1:]),
                            app,
                            name = app.name),
        return urls
        
    def register(self, application):
        if not isinstance(application,Application):
            raise DjpcmsException('Cannot register application. Is is not a valid one.')
        
        if application.name in self._nameregistry:
            raise AlreadyRegistered('Application %s already registered as application' % application)
        self._nameregistry[application.name] = application
        application.register(self)
        model = getattr(application,'model',None)
        if model:
            if model in self._registry:
                raise AlreadyRegistered('Model %s already registered as application' % model)
            self._registry[model] = application
        else:
            pass
    
    def unregister(self, model):
        '''Unregister the :class:`djpcms.views.appsite.ModelApplication registered for *model*. Return the
application class which has been unregistered.'''
        appmodel = self._registry.pop(model,None)
        if appmodel:
            self._nameregistry.pop(appmodel.name,None)
        return None if not appmodel else appmodel.__class__
    
    def clear(self):
        '''Clear the site from all applications'''
        ResolverMixin.clear(self)
        del self.choices[1:]
        self._nameregistry.clear()
        self._registry.clear()
            
    def for_model(self, model):
        '''Obtain a :class:`djpcms.views.appsite.ModelApplication` for model *model*.
If the application is not available, it returns ``None``. Never fails.'''
        try:
            return self._registry.get(model,None)
        except:
            return None
            
    def getapp(self, appname):
        '''Given a *appname* in the form of appname-appview
returns the application handler. If the appname is not available, it raises a KeyError'''
        names = appname.split('-')
        if len(names) == 2:
            name     = names[0]
            app_code = names[1]
            appmodel = self._nameregistry.get(name,None)
            if appmodel:
                return appmodel.getview(app_code)
        appmodel = self._nameregistry.get(appname,None)
        if appmodel is None:
            raise ApplicationNotAvailable('Application {0} not available.'.format(appname))
        return appmodel.root_application
    
    def get_instanceurl(self, instance, view_name = 'view', **kwargs):
        '''Calculate a url given a instance'''
        app = self.for_model(instance.__class__)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
    
    def get_url(self, model, view_name, instance = None, **kwargs):
        if not isinstance(model,type):
            instance = model
            model = instance.__class__
        app = self.for_model(model)
        if app:
            view = app.getview(view_name)
            if view:
                try:
                    return view.get_url(None, instance = instance, **kwargs)
                except:
                    return None
        return None
        
    def count(self):
        return len(self._registry)
    
    def as_wsgi(self):
        return make_wsgi(self)
    
    def _load_middleware(self):
        if self._request_middleware is None:
            self._request_middleware = mw = []
            self._response_middleware = rw = []
            self._exception_middleware = ew = []
            self.lock.acquire()
            try:
                for middleware_path in self.settings.MIDDLEWARE_CLASSES:
                    mwcls = module_attribute(middleware_path)
                    if mwcls:
                        mwobj = mwcls()
                        if hasattr(mwobj,'process_request'):
                            mw.append(mwobj.process_request)
                        if hasattr(mwobj,'process_response'):
                            rw.append(mwobj.process_response)
                        if hasattr(mwobj,'process_exception'):
                            ew.append(mwobj.process_exception)
            finally:
                self.lock.release()
    
    def request_middleware(self):
        self._load_middleware()
        return self._request_middleware
    
    def response_middleware(self):
        self._load_middleware()
        return self._response_middleware
    
    def exception_middleware(self):
        self._load_middleware()
        return self._exception_middleware
    