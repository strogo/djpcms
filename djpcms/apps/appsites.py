from djpcms.core.exceptions import DjpcmsException, AlreadyRegistered, ApplicationNotAvailable
from djpcms.views.appsite import Application, ModelApplication
from djpcms.apps.included.contentedit import ContentSite, BlockContent
from djpcms.utils.collections import OrderedDict
from djpcms.utils.importer import import_module
from djpcms.core.urlresolvers import ResolverMixin
from djpcms.http import make_wsgi



class ApplicationSite(ResolverMixin):
    '''
    Application site manager
    An instance of this class is used to handle url of
    registered applications.
    '''
    def __init__(self, url, config):
        self.route = url
        self.url = url
        self.config = config
        self.settings = config
        self.editavailable = config.CONTENT_INLINE_EDITING.get('available',False)
        self.editurl  = config.CONTENT_INLINE_EDITING.get('preurl','/edit/')
        self._registry = {}
        self._nameregistry = OrderedDict()
        self.choices = [('','-----------------')]
        self.ModelApplication = ModelApplication
        
    def __repr__(self):
        return '{0} - {1}'.format(self.route,'loaded' if self.isloaded else 'not loaded')
    __str__ = __repr__
        
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
        
    def count(self):
        return len(self._registry)
    
    def as_wsgi(self):
        return make_wsgi(self)
    