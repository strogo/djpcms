import os
import djpcms_defaults
from djpcms.utils.importlib import import_module


_novalue = object()


def djpcms_settings_for_django(settings_file):
    settings_module = import_module(settings_file)
    for sett in dir(djpcms_defaults):
        if sett == sett.upper():
            default = getattr(djpcms_defaults, sett)
            val     = getattr(settings_module, sett, _novalue)
            if val is _novalue:
                yield sett,default
                
                
def djpcms_settings():
    for sett in dir(djpcms_defaults):
        if sett == sett.upper():
            default = getattr(djpcms_defaults, sett)
            yield sett,default
            

def _get_settings():
    '''Get settings.'''
    framework_name = getattr(djpcms_defaults,'DJPCMS_WEB_FRAMEWORK','django')
    framework = True
    if framework_name == 'django':
        ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"
        settings_file = os.environ.get(ENVIRONMENT_VARIABLE,None)
        if not settings_file:
            settings_file = 'djpcms.core.defaults.settings'
            os.environ[ENVIRONMENT_VARIABLE] = settings_file
        from django.conf import settings as framework_settings
        djpsettings = djpcms_settings_for_django(settings_file)
    else:
        framework_settings = object()
        djpsettings = djpcms_settings()
    
    # Loop over default djpcms settings
    for sett,val in djpsettings:
        setattr(framework_settings, sett, val)
                
    ajax = framework_settings.HTML_CLASSES
    if not ajax:
        from djpcms.ajaxhtml import ajaxhtml
        framework_settings.HTML_CLASSES = ajaxhtml() 
    return framework_settings


settings = _get_settings()