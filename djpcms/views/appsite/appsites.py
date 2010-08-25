from django.db.models.base import ModelBase
from django import http
from django.utils.datastructures import SortedDict

from djpcms.views.appsite.applications import ApplicationBase, ModelApplication
from djpcms import siteapp_choices


class ApplicationSite(object):
    '''
    Application site manager
    An instance of this class is used as singletone to handle url of
    registered django applications.
    '''
    def __init__(self):
        from djpcms.conf import settings
        self.root_path     = settings.APPLICATION_URL_PREFIX[1:]
        self.editavailable = settings.CONTENT_INLINE_EDITING.get('available',False)
        self._registry     = {}
        self._nameregistry = SortedDict()
        self.choices       = siteapp_choices
        
    def count(self):
        return len(self._registry)
        
    def register(self,
                 baseurl,
                 application_class = None,
                 model = None,
                 editavailable = True,
                 **options):
        """
        Registers an application to a baseurl.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelApplication (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.
        """        
        if isinstance(model, ModelBase):
            model_or_iterable = [model]
        else:
            model_or_iterable = model
            
        if not application_class:
            if not model_or_iterable:
                application_class = ApplicationBase
            else:
                application_class = ModelApplication 
        
        editavailable = self.editavailable and editavailable
        if model_or_iterable:
            for model in model_or_iterable:
                # Instantiate the admin class to save in the registry
                if model in self._registry:
                    raise ValueError('Model %s already registered as application' % model)
                app = application_class(baseurl, self, editavailable, model)
                if app.name in self._nameregistry:
                    raise ValueError('Model %s already registered as application' % model)
                self._registry[model] = app
                self._nameregistry[app.name] = app
        else:
            app = application_class(baseurl, self, editavailable)
            if app.name in self._nameregistry:
                raise ValueError('Application %s already registered as application' % app.name)
            self._nameregistry[app.name] = app
            self.choices.append((app.name,app.name))
    
    def unregister(self, model):
        appmodel = self._registry.pop(model,None)
        if appmodel:
            self._nameregistry.pop(appmodel.name,None)
            
    def for_model(self, model):
        return self._registry.get(model,None)
            
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
                return appmodel.getapp(app_code)
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
