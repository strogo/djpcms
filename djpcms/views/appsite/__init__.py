from django.utils.importlib import import_module
from djpcms.views.appsite.appsites import Application, ModelApplication
from djpcms.views.appsite.appsites import ApplicationSite, site


def load():
    '''Load dynamic applications and create urls
    '''
    from djpcms.conf import settings
    if not site.isloaded:
        if settings.APPLICATION_URL_MODULE:
            app_module = import_module(settings.APPLICATION_URL_MODULE)
            appurls = app_module.appurls
        else:
            appurls = ()
        site.load(*appurls)

