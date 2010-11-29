from djpcms.core.exceptions import DjpcmsException, AlreadyRegistered
from djpcms.views.appsite.applications import Application, ModelApplication
from djpcms.utils.collections import OrderedDict
from djpcms import siteapp_choices


class ApplicationSite(object):
    '''
    Application site manager
    An instance of this class is used as singletone to handle url of
    registered django applications.
    '''
    def __init__(self):
        from djpcms.conf import settings
        self.settings      = settings
        self.editavailable = settings.CONTENT_INLINE_EDITING.get('available',False)
        self.editurl       = settings.CONTENT_INLINE_EDITING.get('preurl','/edit/')
        self._registry     = {}
        self._nameregistry = OrderedDict()
        self.choices       = siteapp_choices
        self.isloaded      = False
        
    def load_initial(self):
        baseurl = self.settings.CONTENT_INLINE_EDITING.get('pagecontent', '/content/')
        from djpcms.views.apps.contentedit import ContentSite, BlockContent
        self.register(ContentSite(baseurl, BlockContent, editavailable = False))
        
    def count(self):
        return len(self._registry)
        
    def load(self, *applications):
        """Registers an instance of :class:`djpcms.views.appsite.Application`
to the site. If a model is already registered, this will raise AlreadyRegistered."""
        if self.isloaded:
            return
        self.load_initial()
        for application in applications:
            self.register(application)
        self.isloaded = True
        
    def register(self, application):
        if not isinstance(application,Application):
            raise DjpcmsException('Cannot register application. Is is not a valid one.')
        
        if application.name in self._nameregistry:
            raise AlreadyRegistered('Application %s already registered as application' % application)
        self._nameregistry[application.name] = application
        
        model = getattr(application,'model',None)
        if model:
            if model in self._registry:
                raise AlreadyRegistered('Model %s already registered as application' % model)
            self._registry[model] = application
        else:
            pass
            #self.choices.append((app.name,app.name))
        application.register(self)
    
    def unregister(self, model):
        '''Unregister the :class:`djpcms.views.appsite.ModelApplication registered for *model*. Return the
application class which has been unregistered.'''
        appmodel = self._registry.pop(model,None)
        if appmodel:
            self._nameregistry.pop(appmodel.name,None)
        return None if not appmodel else appmodel.__class__
    
    def clear(self):
        '''Clear the site from all applications'''
        del self.choices[1:]
        self._nameregistry.clear()
        self._registry.clear()
        self.isloaded = False
            
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
        from django.db import models
        names = appname.split('-')
        if len(names) == 2:
            name     = names[0]
            app_code = names[1]
            appmodel = self._nameregistry.get(name,None)
            if appmodel:
                return appmodel.getview(app_code)
        appmodel = self._nameregistry.get(appname,None)
        if appmodel is None:
            raise KeyError('Application %s not available.' % appname)
        return appmodel.root_application
    
    def count(self):
        return len(self._registry)
            
    def get_urls(self):
        from django.conf.urls.defaults import url
        urls = ()
        # Add in each model's views.
        for app in self._nameregistry.values():
            baseurl = app.baseurl
            if baseurl:
                urls += url(regex = '^%s(.*)' % baseurl[1:],
                            name = app.name,
                            view = app),
        return urls    
        
        
site = ApplicationSite()
