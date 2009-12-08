import os
import logging
import copy

from django.utils.safestring import mark_safe
from djpcms.utils.plugin import PluginBase, loadobjects
from djpcms.utils import json, form_kwargs
from djpcms.utils.formjson import form2json
    

_plugin_dictionary = {}
_wrapper_dictionary = {}


def plugingenerator():
    for p in _plugin_dictionary.values():
        yield (p.name,p.description)
        
def wrappergenerator():
    for p in _wrapper_dictionary.values():
        yield (p.name,p.description)

        
def get_plugin(name, default = None):
    return _plugin_dictionary.get(name,default)

def get_wrapper(name, default = None):
    return _wrapper_dictionary.get(name,default)


def register_application(app):
    ApplicationPlugin(app).register()

def loadplugins(plist):
    EmptyPlugin().register()
    ThisPlugin().register()
    loadobjects(plist,DJPplugin)
    
def loadwrappers(plist):
    loadobjects(plist,DJPwrapper)


####    IMPLEMENTATION





class DJPpluginMeta(type):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    pass

class DJPwrapperMeta(type):
    '''
    Just a metaclass to differentiate wrapper from other calsses
    '''
    pass


class DJPwrapper(PluginBase):
    '''
    Class responsible for wrapping djpcms plugins
    '''
    __metaclass__ = DJPwrapperMeta
    form_layout   = None
    storage       = _wrapper_dictionary

    def wrap(self, djp, cblock, html):
        '''
        Render the inner block. This function is the one to implement
        '''
        if html:
            return html
        else:
            return u''
    
    def __call__(self, djp, cblock, html):
        '''
        Wrap content for block cblock
        @param param: djp instance of djpcms.views.baseview.DjpRequestWrap 
        @param param: cblock instance or BlockContent
        @return: safe unicode HTML
        '''
        return mark_safe(u'\n'.join(['<div class="djpcms-block-element">',
                                     self.wrap(djp, cblock, html),
                                     '</div>']))


class DJPplugin(PluginBase):
    '''
    Base class for plugins
    '''
    __metaclass__ = DJPpluginMeta
    form          = None
    withrequest   = False
    edit_form     = False
    storage       = _plugin_dictionary
    
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
           
class SimpleWrap(DJPwrapper):
    name         = 'simple no-tag'
    

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
    
                    

default_content_wrapper = SimpleWrap().register()
