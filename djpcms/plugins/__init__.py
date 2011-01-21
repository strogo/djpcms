import os
import logging
import json

from djpcms import forms
from djpcms.forms.utils import form_kwargs
from djpcms.utils import force_str
from djpcms.utils.text import capfirst, nicename
from djpcms.utils.formjson import form2json

_plugin_dictionary = {}
_wrapper_dictionary = {}


def ordered_generator(di):
    cmp = lambda x,y : 1 if x.description > y.description else -1
    def _():
        return ((c.name,c.description) for c in sorted(di.values(),cmp))
    return _


plugingenerator  = ordered_generator(_plugin_dictionary)
wrappergenerator = ordered_generator(_wrapper_dictionary)
get_plugin = lambda name, default = None:  _plugin_dictionary.get(name,default)
get_wrapper = lambda name, default = None: _wrapper_dictionary.get(name,default)


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


class DJPpluginMetaBase(forms.MediaDefiningClass):
    '''
    Just a metaclass to differentiate plugins from other calsses
    '''
    def __new__(cls, name, bases, attrs):
        new_class = super(DJPpluginMetaBase, cls).__new__
        if attrs.pop('virtual',None) or not attrs.pop('auto_register',True):
            return new_class(cls, name, bases, attrs)
        pname = attrs.get('name',None)
        if pname is None:
            pname = name
        pname = pname.lower()
        descr = attrs.get('description',None)
        if not descr:
            descr = pname
        if pname != '':
            descr = nicename(descr) 
        attrs['name'] = pname
        attrs['description'] = descr
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


class DJPwrapper(object):
    '''Class responsible for wrapping :ref:`djpcms plugins <plugins-index>`.
    '''
    __metaclass__ = DJPwrapperMeta
    
    virtual       = True
    
    name          = None
    '''Unique name. If not provided the class name will be used. Default ``None``.'''
    form_layout   = None

    def wrap(self, djp, cblock, html):
        '''Wrap content for block and return safe HTML.
This function should be implemented by derived classes.
        
* *djp* instance of :class:`djpcms.views.response.DjpResponse`.
* *cblock* instance of :class:'djpcms.models.BlockContent`.
* *html* safe unicode string of inner HTML.'''
        return html if html else ''
    
    def __call__(self, djp, cblock, html):
        name  = cblock.plugin_name
        id    = cblock.htmlid()
        head  = '<div id="{0}" class="djpcms-block-element plugin-{1}">\n'.format(id,name)
        inner = self.wrap(djp, cblock, html)
        return head + inner + '\n</div>'
    
    def _register(self):
        global _wrapper_dictionary
        _wrapper_dictionary[self.name] = self


class DJPplugin(object):
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
    '''Form class for editing the plugin parameters. Default ``None``, the plugin has no arguments.'''
    form_withrequest = False
    '''Equivalent to :attr:`djpcms.views.appsite.ModelApplication.form_withrequest`. If set to ``True``,
    the ``request`` instance is passed to the :attr:`form` constructor. Default is ``False``.'''
    permission      = 'authenticated'
    #storage       = _plugin_dictionary
    #URL           = None
    
    def js(self, **kwargs):
        '''Function which can be used to inject javascript dynamically.'''
        return None
    
    def css(self):
        '''Function which can be used to inject css dynamically.'''
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
        kwargs.update(**self.arguments(args))
        return self.edit_form(djp, **kwargs)
        
    def edit_form(self, djp, **kwargs):
        '''Returns the form used to edit the plugin **content**. Most plugins don't need to implement this
        functions but some do. Check
        the :class:`djpcms.plugins.text.Text` for example. By default it returns ``None``.'''
        return None
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''Render the plugin. It returns a safe string to be included in the HTML page.
This is the function plugins need to implement.

* *djp* instance of :class:`djpcms.views.response.DjpResponse`.
* *wrapper* :class:`DJPwrapper` instance which wraps the plugin.
* *prefix* a prefix string or ``None`` to use for forms within the plugin.
* *kwargs* plugin specific key-valued arguments.'''
        return ''
    
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
                                           withdata = withdata,
                                           own_view = djp.own_view()))
            
    #def response(self, request, *bits):
    #    raise http.Http404
    
    def _register(self):
        global _plugin_dictionary
        _plugin_dictionary[self.name] = self
        
    def __eq__(self, other):
        if isinstance(other,DJPplugin):
            return self.name == other.name
        return False
    

class EmptyPlugin(DJPplugin):
    '''
    This is the empty plugin. It render nothing
    '''
    name         = ''
    description  = '--------------------'
    

class ThisPlugin(DJPplugin):
    '''Current view plugin. This plugin render the current view
only if it is an instance of :class:`djpcms.views.appview.AppViewBase`.
For example if the current view is a :class:`djpcms.views.appview.SearchView`,
the plugin will display the search view for that application.
    '''
    name        = 'this'
    description = 'Current View'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        djp.wrapper = wrapper
        djp.prefix  = prefix
        return djp.view.render(djp)
    
    
class ApplicationPlugin(DJPplugin):
    '''Plugin formed by :class:`djpcms.views.appview.AppViewBase` classes
which have the :attr:`djpcms.views.appview.AppViewBase.isplugin` attribute
set to ``True``.

For example, lets say an application as a :class:`djpcms.views.appview.AddView` view
which is registered to be a plugin, than it will be managed by this plugin.'''
    auto_register = False
    
    def __init__(self, app, name = None, description = None):
        global _plugin_dictionary
        self.app  = app
        self.form = app.plugin_form
        if not name:
            name = '%s-%s' % (app.appmodel.name,app.name)
        if not description:
            description = app.description or name
        self.name = name
        self.description = nicename(description)
        _plugin_dictionary[self.name] = self
        
    def render(self, djp, wrapper, prefix, **kwargs):
        #kwargs may be an input from a possible plugin form
        app  = self.app
        request = djp.request
        html = u''
        if app.has_permission(request):
            if djp.view != app or kwargs:
                args = djp.kwargs.copy()
                args.update(kwargs)
                t_djp = self.app(djp.request, **args)
            else:
                t_djp = djp
            t_djp.wrapper = wrapper
            t_djp.prefix  = prefix
            html = self.app.render(t_djp)
            # Add media. It must be after having called render!!
            if djp != t_djp:
                djp.media += t_djp.media
        return html
    

class SimpleWrap(DJPwrapper):
    name         = 'simple no-tags'

default_content_wrapper = SimpleWrap()
