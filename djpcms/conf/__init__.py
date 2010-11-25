import os
import djpcms_defaults


def _get_settings():
    framework = os.environ.get('DJPCMS_WEB_FRAMEWORK','django')
    if framework == 'django':
        if not os.environ.get('DJANGO_SETTINGS_MODULE',None):
            os.environ['DJANGO_SETTINGS_MODULE'] = 'djpcms.core.defaults.settings'
        from django.conf import settings as framework_settings
    else:
        raise ValueError('Framework %s not supported' % framework)
    
    for sett in dir(djpcms_defaults):
        if sett == sett.upper():
            default = getattr(djpcms_defaults, sett)
            val     = getattr(framework_settings, sett, default)
            setattr(framework_settings, sett, val)
    ajax = framework_settings.HTML_CLASSES
    if not ajax:
        from djpcms.ajaxhtml import ajaxhtml
        framework_settings.HTML_CLASSES = ajaxhtml() 
    return framework_settings


settings = _get_settings()