import os
import logging
import copy

from django import http, forms
from django.utils.safestring import mark_safe
from djpcms.utils.plugin import PluginBase, loadobjects
from djpcms.utils import json, form_kwargs
from djpcms.utils.formjson import form2json
from djpcms.utils.deco import response_wrap
from djpcms.conf import settings
    

_plugin_dictionary = {}
_wrapper_dictionary = {}

def ordered_generator(di):
    def cmp(x,y):
        if x.description > y.description:
            return 1
        else:
            return -1
    ordered = sorted(di.values(),cmp)
    for c in ordered:
        yield (c.name,c.description)

def plugingenerator():
    return ordered_generator(_plugin_dictionary)
        
def wrappergenerator():
    return ordered_generator(_wrapper_dictionary)
        
def get_plugin(name, default = None):
    return _plugin_dictionary.get(name,default)

def get_wrapper(name, default = None):
    return _wrapper_dictionary.get(name,default)

def register_application(app, name = None, description = None):
    '''
    Register an application view as a plugin
    app is instance of an application view
    '''
    if hasattr(app,'get_plugin'):
        p = app.get_plugin()
    else:
        p = ApplicationPlugin(app,name,description)
    media = p.media + app.get_media()
    p.__class__.media = media
    p.register()


def loadplugins(plist):
    '''
    Load plugins into the global plugin dictionary
    '''
    EmptyPlugin().register()
    ThisPlugin().register()
    loadobjects(plist,DJPplugin)
    urls = []
    for p in _plugin_dictionary.values():
        if p.URL:
            urls.append((r'^%s' % p.URL.lstrip('/'), p.response))
    #urls.append((r'^%s([\w/-]*)' % settings.DJPCMS_PLUGIN_BASE_URL.lstrip('/'), generic_plugin_response))
    return tuple(urls)


def loadwrappers(plist):
    loadobjects(plist,DJPwrapper)


@response_wrap
def generic_plugin_response(request, url):
    '''
    Handle plugin response
    '''
    url  = url.rstrip('/')
    bits = url.split('/')
    name = bits.pop(0)
    plugin = _plugin_dictionary.get(name,None)
    if not plugin:
        raise http.Http404
    else:
        return plugin.response(request, *tuple(bits))





####    IMPLEMENTATION

class DJPpluginMeta(forms.MediaDefiningClass):
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
    Base class for Plug-ins.
    At a glance
     1) A Plug-in is dynamic application
     2) It is rendered within a djpcms content block
     3) Each content block display a plug-in
     4) A plug-in can define style to include in the page
     5) It can also add script to the page
     6) It can have parameters to control its behaviour
    '''
    __metaclass__ = DJPpluginMeta
    form          = None
    withrequest   = False
    edit_form     = False
    storage       = _plugin_dictionary
    URL           = None
    
    def js(self, **kwargs):
        return None
    
    def css(self):
        return None
    
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
        
    def __get_url(self):
        if self.URL:
            return self.URL
        else:
            return '%s%s/' % (settings.DJPCMS_PLUGIN_BASE_URL,self.__class__.name)
    url = property(__get_url)
        
    def processargs(self,kwargs):
        '''
        You can use this hook to perform pre-processing on parameters
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
            
    def response(self, request, *bits):
        raise http.Http404
    
    
    
           
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
    def __init__(self, app, name = None, description = None):
        self.app  = app
        try:
            opts = app.appmodel.model._meta
        except:
            opts = None
        if not name:
            self.name = '%s %s' % (app.appmodel.name,app.name)
        else:
            self.name = name
        if not description:
            self.description = u'%s %s' % (opts.verbose_name, app.name)
        else:
            self.description = description
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        This function needs to be implemented
        '''
        app  = self.app
        request = djp.request
        if app.has_permission(request):
            if djp.view != app:
                args = copy.copy(djp.urlargs)
                args.update(kwargs)
                t_djp = self.app(djp.request, **args)
            else:
                t_djp = djp
            djp.wrapper = wrapper
            djp.prefix  = prefix
            html = self.app.render(t_djp)
            if djp is not t_djp:
                djp.media += t_djp.media
            return html
        else:
            return ''
        #args = copy.copy(djp.urlargs)
        #args.update(kwargs)
        # Application plugin with instance are not supported!!
        #instance = args.pop('instance',None)
        #if instance and not isinstance(instance,app.model):
        #    instance = None 
        #ndjp = self.app(djp.request, instance = instance, **args)
        #ndjp.wrapper = wrapper
        #ndjp.prefix  = prefix
        #if app.has_permission(request):
        #    return self.app.render(ndjp)
        #else:
        #    return ''
    
                    

default_content_wrapper = SimpleWrap().register()
