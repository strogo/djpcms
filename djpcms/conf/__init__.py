import os

from djpcms.conf import djpcms_defaults
from djpcms.utils.importer import import_module
from djpcms.ajaxhtml import ajaxhtml


class NoData(object):
    def __repr__(self):
        return '<NoData>'
    __str__ = __repr__
    
nodata = NoData()


class DjpcmsConfig(object):
    
    def __init__(self, settings_module_name, **kwargs):
        self.__dict__['_values'] = {}
        self.__dict__['_settings'] = []
        self.__dict__['settings_module_name'] = settings_module_name
        self.fill(djpcms_defaults)
        if self.settings_module_name:
            settings_module = import_module(settings_module_name)
            self.fill(settings_module)
        self.update(kwargs)
        ajax = self.HTML_CLASSES
        if not ajax:
            self.HTML_CLASSES = ajaxhtml()
        
    def __repr__(self):
        return self._values.__repr__()
    __str__  = __repr__
    
    def update(self, mapping):
        v = self._values
        for sett,val in mapping.items():
            if sett == sett.upper():
                v[sett] = val
   
    def fill(self, mod, override = True):
        v = self._values
        for sett in dir(mod):
            if sett == sett.upper():
                default = v.get(sett, nodata)
                val     = getattr(mod, sett)
                if default is nodata or override:
                    v[sett] = val
                    
            
    def addsetting(self, setting):
        self._settings.append(setting)
        self.fill(setting,False)
        for sett,value in self._values.items():
            setattr(setting,sett,value)
        
    def __getattr__(self, name):
        try:
            return self._values[name]
        except KeyError:
            raise AttributeError('Attribute {0} not available'.format(name))
    
    def __setattr__(self, name, value):
        self._values[name] = value
        for sett in self._settings:
            setattr(sett,name,value)
        
        
class SettingImporter(object):
    
    def get_settings(self, settings_module_name = None, **kwargs):
        '''Get settings module for a site.'''
        config = DjpcmsConfig(settings_module_name, **kwargs)
        self.setup_django(config)
        return config
    
    def setup_django(self, config):
        '''Set up django if needed'''
        if config.DJPCMS_WEB_FRAMEWORK == 'django' or config.HTTP_LIBRARY == 'django' or \
                config.CMS_ORM == 'django' or config.TEMPLATE_ENGINE == 'django':
            ENVIRONMENT_VARIABLE = "DJANGO_SETTINGS_MODULE"
            settings_file = os.environ.get(ENVIRONMENT_VARIABLE,None)
            if not settings_file:
                settings_file = 'djpcms.apps.djangosite.settings'
            os.environ[ENVIRONMENT_VARIABLE] = settings_file
            
            from django.conf import settings as framework_settings
            config.addsetting(framework_settings)


_importer = SettingImporter()

get_settings = _importer.get_settings
