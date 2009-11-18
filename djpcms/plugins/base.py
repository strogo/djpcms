from djpcms.utils import form_kwargs

_plugin_dictionary = {}



class DJPplugin(object):
    name         = None
    description  = None
    form         = None
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

register_plugin(EmptyPlugin)
register_plugin(ThisPlugin)