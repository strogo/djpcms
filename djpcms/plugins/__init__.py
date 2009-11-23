import os
import glob
import logging
import copy

from djpcms.utils import json
from djpcms.utils import form_kwargs
from djpcms.utils.formjson import form2json

from wrapper import *

log = logging.getLogger("djpcms.plugins")



_plugin_dictionary = {}


class DJPpluginMeta(type):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    pass



class DJPplugin(object):
    '''
    Base class for plugins
    '''
    __metaclass__ = DJPpluginMeta
    name          = None
    description   = None
    form          = None
    virtual       = False
    withrequest   = False
    edit_form     = False
    
    def arguments(self, args):
        '''
        Process arguments string
        '''
        try:
            kwargs = json.loads(args)
            if isinstance(kwargs,dict):
                rargs = {}
                for k,v in kwargs.items():
                    rargs[str(k)] = v
                return self.processargs(rargs)
            else:
                return {}
        except:
            return {}
        
    def processargs(self,kwargs):
        '''
        You can use this hook to perfom some preprocessing on options
        '''
        return kwargs
    
    def __call__(self, djp, args = None, wrapper = None, prefix = None):
        '''
        This function needs to be implemented
        '''
        return self.render(djp, wrapper, prefix, **self.arguments(args))
    
    def edit(self, djp, args = None, **kwargs):
        if self.edit_form:
            kwargs.update(**self.arguments(args))
            return self.edit_form(djp, **kwargs)
    
    def render(self, djp, wrapper, prefix, **kwargs):
        return u''
    
    def save(self, pform):
        return form2json(pform)
    
    def get_form(self, djp, args = None):
        '''
        Form for this plugin
        '''
        initial = self.arguments(args) or None
        if self.form:
            return self.form(**form_kwargs(request = djp.request,
                                           initial = initial,
                                           withrequest = self.withrequest))
           
    

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
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        This function needs to be implemented
        '''
        djp.wrapper = wrapper
        djp.prefix  = prefix
        return djp.view.render(djp)
    
    
class ApplicationPlugin(DJPplugin):
    '''
    Plugin formed by application views
    '''
    def __init__(self, app):
        self.app  = app
        self.name = '%s %s' % (app.appmodel.name,app.name)
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        This function needs to be implemented
        '''
        app  = self.app
        args = copy.copy(djp.urlargs)
        args.update(kwargs)
        instance = args.pop('instance',None)
        if instance and not isinstance(instance,app.model):
            instance = None 
        ndjp = self.app.requestview(djp.request,
                                    instance = instance,
                                    **args)
        ndjp.wrapper = wrapper
        ndjp.prefix  = prefix
        return self.app.render(ndjp)
    
    
    

def functiongenerator():
    '''
    generator for iterating through rendering functions.
    Used in django.Forms
    '''
    for p in _plugin_dictionary.values():
        yield (p.name,p.description)


def register_application(app):
    p = ApplicationPlugin(app)
    register_plugin(p)
    
def register_plugin(plugin):
    '''
    Register a new plugin object
    '''
    name = plugin.name
    if name is None:
        name = plugin.__name__
        plugin.name = name
    plugin.description = plugin.description or name
    if isinstance(plugin,DJPpluginMeta):
        plugin = plugin()
    if not _plugin_dictionary.has_key(name):
        _plugin_dictionary[name] = plugin
        
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