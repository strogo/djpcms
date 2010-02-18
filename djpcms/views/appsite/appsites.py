from django.db.models.base import ModelBase
from django import http
from django.utils.datastructures import SortedDict

from djpcms.views.appsite.options import ModelApplication
from djpcms import siteapp_choices


class ApplicationSite(object):
    '''
    Application site manager
    An instance of this class is used as singletone to handle url of
    registered django applications.
    '''
    def __init__(self):
        from djpcms.settings import APPLICATION_URL_PREFIX, CONTENT_INLINE_EDITING
        self.root_path     = APPLICATION_URL_PREFIX[1:]
        self.editavailable = CONTENT_INLINE_EDITING.get('available',False)
        self._registry     = {}
        self._nameregistry = SortedDict()
        self.parent_pages  = {}
        self.root_pages    = {}
        self.choices       = siteapp_choices
        
    def count(self):
        return len(self._registry)
        
    def register(self, model_or_iterable, application_class=None,
                 editavailable = True, **options):
        """
        Registers the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelApplication (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.
        """
        if not application_class:
            application_class = ModelApplication
        
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        
        editavailable = self.editavailable and editavailable
        if model_or_iterable:
            for model in model_or_iterable:
                # Instantiate the admin class to save in the registry
                if model in self._registry:
                    raise ValueError('Model %s already registered as application' % model)
                appmodel = application_class(model, self, editavailable)
                if appmodel.name in self._nameregistry:
                    raise ValueError('Model %s already registered as application' % model)
                self._registry[model] = appmodel
                self._nameregistry[appmodel.name] = appmodel
        else:
            app = application_class()
            if app.name in self._nameregistry:
                raise ValueError('Application %s already registered as application' % app.name)
            self._nameregistry[app.name] = app
            self.choices.append((app.name,app.name))
            
    def for_model(self, model):
        return self._registry.get(model,None)
            
    def getapp(self, appname):
        '''
        Given a appname in the form of app_label-model_name-app_code
        returns the application handler
        '''
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
            raise ValueError('Application name %s not recognized' % appname)
        return appmodel
    
    def count(self):
        return len(self._registry)
            
    def get_urls(self):
        aurls = []
        # Add in each model's views.
        for app in self._nameregistry.values():
            urls = app.make_urls()
            if urls:
                aurls.extend(urls)
        return tuple(aurls)
    urls = property(fget = get_urls)
    
        
        
site = ApplicationSite()
