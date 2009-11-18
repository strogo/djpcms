import os
import glob
import logging

from djpcms.utils import form_kwargs
from wrapper import *

log = logging.getLogger("djpcms.plugins")



_plugin_dictionary = {}


class DJPpluginMeta(type):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    pass

class DJPplugin(object):
    __metaclass__ = DJPpluginMeta
    name         = None
    description  = None
    form         = None
    virtual      = False
    withrequest  = False
    
    def arguments(self, args):
        return {}
        
    def __call__(self, djp, args):
        '''
        This function needs to be implemented
        '''
        return self.render(djp, **self.arguments(args))
    
    def render(self, djp, **kwargs):
        return u''
    
    def get_form(self, djp):
        '''
        Form for this plugin
        '''
        if self.form:
            return self.form(**form_kwargs(request = djp.request, withrequest = self.withrequest))
    

class EmptyPlugin(DJPplugin):
    '''
    This is the empty plugin. It render nothing
    '''
    name         = ''
    description  = '--------------------'
    

class ThisPlugin(DJPplugin):
    '''
    Current view plugin. This plugin render the current view
    The view must be a AppView instance
    @see: sjpcms.views.appview
    '''
    name        = 'this'
    description = 'Current View'
    
    def render(self, djp, **kwargs):
        '''
        This function needs to be implemented
        '''
        return u''
    
    def get_form(self, djp):
        '''
        Form for this plugin
        '''
        return None
    

def functiongenerator():
    '''
    generator for iterating through rendering functions.
    Used in django.Forms
    '''
    for p in _plugin_dictionary.values():
        yield (p.name,p.description)

    
def register_plugin(plugin):
    '''
    Register a new plugin object
    '''
    name = plugin.name
    if name is None:
        name = plugin.__name__
        plugin.name = name
    plugin.description = plugin.description or name
    if not _plugin_dictionary.has_key(name):
        _plugin_dictionary[name] = plugin()
        
def get_plugin(name):
    return _plugin_dictionary.get(name,None)


def loadplugins(plist):
    '''
    Load plugins into cache.
    Called by djpcms.urls
    '''
    register_plugin(EmptyPlugin)
    register_plugin(ThisPlugin)
    for plugin in plist:
        if plugin.endswith('.*'):
            to_load = expand_star(plugin)
        else:
            to_load = [plugin]
        for p in to_load:
            try:
                mod = __import__(p, '', '', [''])
            except ImportError, e:
                log.error("Couldn't import provider %r: %s" % (p, e))
            else:
                for name in dir(mod):
                    obj = getattr(mod, name)
                    if isinstance(obj,DJPpluginMeta) and not obj == DJPplugin and not obj.virtual:
                        register_plugin(obj)
                
def expand_star(mod_name):
    """
    Expand something like 'djpcms.plugins.*' into a list of all the modules
    there.
    """
    expanded = []
    mod_dir = os.path.dirname(__import__(mod_name[:-2], {}, {}, ['']).__file__)
    for f in glob.glob1(mod_dir, "[!_]*.py"):
        expanded.append('%s.%s' % (mod_name[:-2], f[:-3]))
    return expanded