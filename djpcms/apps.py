import os
import sys


def MakeSite(name, settings = 'settings'):
    '''Initialise DjpCms from a directory or a file'''
    import djpcms
    from djpcms.utils.importlib import import_module
    #
    # if not a directory it may be a file
    if not os.path.isdir(name):
        try:
            mod = import_module(name)
            appdir = mod.__path__[0]
        except ImportError:
            if not os.path.isfile(name):
                raise ValueError('Could not find directory or file {0}'.format(name))
            appdir = os.path.split(os.path.realpath(name))[0]
    else:
        appdir = name
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
    djpcms.init_logging()
    return get_site()
    

def get_site():
    from djpcms.views import appsite
    return appsite.site

    
def get_url(model, view_name, instance = None, **kwargs):
    from djpcms.views.appsite import site
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