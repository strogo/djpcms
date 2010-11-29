import os
import djpcms_defaults

ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"

_novalue = object()

def _get_settings():
    '''Get settings.
This function sucks but unfortunately we still depends on django. We will get there :)
'''
    framework_name = getattr(djpcms_defaults,'DJPCMS_WEB_FRAMEWORK','django')
    framework = True
    if framework_name == 'django':
        if not os.environ.get(ENVIRONMENT_VARIABLE,None):
            os.environ[ENVIRONMENT_VARIABLE] = 'djpcms.core.defaults.settings'
            framework = False
        from django.conf import settings as framework_settings
    else:
        framework_settings = object()
        framework = False
    
    # Loop over default djpcms settings
    for sett in dir(djpcms_defaults):
        if sett == sett.upper():
            default = getattr(djpcms_defaults, sett)
            val     = getattr(framework_settings, sett, _novalue)
            if val is _novalue:
                setattr(framework_settings, sett, default)
            elif framework:
                setattr(framework_settings, sett, val)
                
    ajax = framework_settings.HTML_CLASSES
    if not ajax:
        from djpcms.ajaxhtml import ajaxhtml
        framework_settings.HTML_CLASSES = ajaxhtml() 
    return framework_settings


settings = _get_settings()