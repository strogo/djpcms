import os
import logging
import copy

from django import http, forms
from django.utils.text import capfirst

from djpcms.utils import UnicodeObject, force_unicode, json, form_kwargs, mark_safe
from djpcms.utils.formjson import form2json
from djpcms.utils.deco import response_wrap

_plugin_dictionary = {}
_wrapper_dictionary = {}

nicename = lambda name : force_unicode(capfirst(name.replace('-',' ').replace('_',' ')))

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
    '''Register an application view as a plugin
* *app* is an instance of an :class:`djpcms.views.appview.AppViewBase`
* *name* name for this plugin'''
    global _plugin_dictionary
    if hasattr(app,'get_plugin'):
        p = app.get_plugin()
    else:
        p = ApplicationPlugin(app)
    #media = p.media + app.get_media()
    #p.__class__.media = media
    #p.register()


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

class DJPpluginMetaBase(forms.MediaDefiningClass):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(DJPpluginMetaBase, cls).__new__
        if attrs.pop('virtual',None) or not attrs.pop('auto_register',True):
            return new_class(cls, name, bases, attrs)
        pname = attrs.get('name',None)
        if not pname:
            pname = name
        pname = pname.lower()
        descr = attrs.get('description',None)
        if not descr:
            descr = pname
        attrs['name'] = pname
        attrs['description'] = nicename(descr)
        pcls = new_class(cls, name, bases, attrs)
        pcls()._register()
        return pcls


class DJPpluginMeta(DJPpluginMetaBase):
    '''
    Just a metaclass to differentiate plugins from other classes
    '''

class DJPwrapperMeta(DJPpluginMetaBase):
    '''
    Just a metaclass to differentiate wrapper from other classes
    '''


class DJPwrapper(UnicodeObject):
    '''Class responsible for wrapping :ref:`djpcms plugins <plugins-class>`.
    '''
    __metaclass__ = DJPwrapperMeta
    form_layout   = None

    def wrap(self, djp, cblock, html):
        '''Wrap content for block and return safe HTML.
This function should be implemented by derived classes.
        
* *djp* instance of :class:`djpcms.views.response.DjpResponse`.
* *cblock* instance of :class:'djpcms.models.BlockContent`.
* *html* safe unicode string of inner HTML.'''
        if html:
            return html
        else:
            return u''
    
    def __call__(self, djp, cblock, html):
        return mark_safe(u'\n'.join(['<div class="djpcms-block-element">',
                                     self.wrap(djp, cblock, html),
                                     '</div>']))
    
    def _register(self):
        global _wrapper_dictionary
        _wrapper_dictionary[self.name] = self


class DJPplugin(UnicodeObject):
    '''Base class for Plugins. These classes are used to display contents on a ``djpcms`` powered site.
The basics:
    
* A Plugin is dynamic application.
* It is rendered within a :class:`DJPwrapper` and each :class:`DJPwrapper` displays a plugin.
* It can define style and javascript to include in the page, in a static way (as a ``meta`` property of the class) or in a dynamic way by member functions.
* It can have parameters to control its behaviour.'''
    __metaclass__ = DJPpluginMeta
    
    virtual       = True
    '''If set to true, the class won't be registered with the plugin's dictionary. Default ``False``.'''
    name          = None
    '''Unique name. If not provided the class name will be used. Default ``None``.'''
    description   = None
    '''A short description to display in forms.'''
    form          = None
    '''Form class for editing the plugin. Default ``None``, the plugin has no arguments.'''
    form_withrequest = False
    '''Equivalent to :attr:`djpcms.views.appsite.ModelApplication.form_withrequest`. If set to ``True``,
    the ``request`` instance is passed to the form constructor. Default is ``False``.'''
    edit_form     = False
    #storage       = _plugin_dictionary
    #URL           = None
    
    def js(self, **kwargs):
        return None
    
    def css(self):
        return None
    
    def arguments(self, args):
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
        
    def processargs(self, kwargs):
        '''You can use this hook to perform pre-processing on plugin parameters if :attr:`form` is set.
By default do nothing.
        '''
        return kwargs
    
    def __call__(self, djp, args = None, wrapper = None, prefix = None):
        return self.render(djp, wrapper, prefix, **self.arguments(args))
    
    def edit(self, djp, args = None, **kwargs):
        if self.edit_form:
            kwargs.update(**self.arguments(args))
            return self.edit_form(djp, **kwargs)
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''Render the plugin. It returns a safe string to be included in the HTML page.
This is the function plugins need to implement.

* *djp* instance of :class:`djpcms.views.response.DjpResponse`.
* *wrapper* :class:`DJPwrapper` instance which wraps the plugin.
* *prefix* a prefix string or ``None`` to use for forms within the plugin.
* *kwargs* plugin specific key-valued arguments.'''
        return u''
    
    def save(self, pform):
        '''Save the form plugin'''
        return form2json(pform)
    
    def get_form(self, djp, args = None, withdata = True):
        '''Return an instance of a :attr:`form` or `None`. Used to edit the plugin when in editing mode.
Usually, there is no need to override this function. If your plugin needs input parameters when editing, simple set the
:attr:`form` attribute.
        '''
        if self.form:
            initial = self.arguments(args) or None
            return self.form(**form_kwargs(request = djp.request,
                                           initial = initial,
                                           withrequest = self.form_withrequest,
                                           withdata = withdata))
            
    #def response(self, request, *bits):
    #    raise http.Http404
    
    def _register(self):
        global _plugin_dictionary
        _plugin_dictionary[self.name] = self
    

class EmptyPlugin(DJPplugin):
    '''
    This is the empty plugin. It render nothing
    '''
    name         = ''
    description  = '--------------------'
    

class ThisPlugin(DJPplugin):
    '''Current view plugin. This plugin render the current view
    The view must be a AppView instance
    @see: sjpcms.views.appview
    '''
    name        = 'this'
    description = 'Current View'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        djp.wrapper = wrapper
        djp.prefix  = prefix
        return djp.view.render(djp)
    
    
class ApplicationPlugin(DJPplugin):
    '''Plugin formed by application views
    '''
    auto_register = False
    
    def __init__(self, app, name = None, description = None):
        global _plugin_dictionary
        self.app  = app
        if not name:
            name = '%s-%s' % (app.appmodel.name,app.name)
        if not description:
            description = app.description or name
        self.name = name
        self.description = nicename(description)
        _plugin_dictionary[self.name] = self
    
    def render(self, djp, wrapper, prefix, **kwargs):
        app  = self.app
        request = djp.request
        if app.has_permission(request):
            if djp.view != app:
                args = copy.copy(djp.kwargs)
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
    

class SimpleWrap(DJPwrapper):
    name         = 'simple no-tags'

default_content_wrapper = SimpleWrap()
