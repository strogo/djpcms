import os
import sys


def MakeSite(name, settings = 'settings'):
    '''Initialise DjpCms from a directory'''
    from djpcms.utils.importlib import import_module
    # if not a directory it may be a file
    if not os.path.isdir(name):
        if not os.path.isfile(name):
            raise ValueError('Could not find directory or file {0}'.format(name))
        path = os.path.realpath(name)
    path = os.path.realpath(name)
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
    from djpcms.views import appsite
    return appsite.site
    

def UnukServe(port = 9011, secure = None):
    from unuk.contrib.txweb import start, djangoapp
    from djpcms.views.appsite import site
    #if secure:
    #    secure = (os.path.join(locdir,secure,'server.key'),
    #              os.path.join(locdir,secure,'server.crt'))
    app =  djangoapp.ApplicationServer(site.settings.SITE_DIRECTORY,
                                       port = port,
                                       secure = secure)
    start()
    
    
def get_url(model, view_name, **kwargs):
    from djpcms.views.appsite import site
    app = site.for_model(model)
    if app:
        view = app.getview(view_name)
        if view:
            try:
                return view.get_url(None,**kwargs)
            except:
                return None
    return None