from djpcms import sites


def handle(engine = None):
    engine = engine or sites.settings.TEMPLATE_ENGINE
    if engine not in _handlers:
        handle = get_engine(engine)
        _handlers[engine] = handle
    else:
        handle = _handlers[engine]
    return handle
        
        
def get_engine(engine, config = None):
    config = config or sites.settings
    if engine == 'django':
        from ._django import TemplateHandler
    elif engine == 'jinja2':
        from ._jinja2 import TemplateHandler
    elif engine == 'cheetah':
        raise NotImplementedError("Cheetah not yet supported.")
    elif engine == 'mustache':
        raise NotImplementedError("Mustache not yet supported.")
    else:
        raise NotImplementedError
    return TemplateHandler(config)


class BaseTemplateHandler(object):

    def setup(self):
        raise NotImplementedError
    
    def get_processors(self, request):
        processors = request.site.settings.TEMPLATE_CONTEXT_PROCESSORS
        return ()
    
    def context(self,
                dict=None, request = None,
                processors=None, current_app=None,
                autoescape=False):
        c = self.context_class(dict, current_app=current_app, autoescape=autoescape)
        if request:
            if processors is None:
                processors = ()
            else:
                processors = tuple(processors)
            for processor in self.get_processors(request) + processors:
                c.update(processor(request))
        return c
    
    @property
    def template_class(self):
        return handle().template_class
    
    @property
    def context_class(self):
        return handle().context_class
    
    def escape(self, html):
        return handle().escape(html)
    
    def conditional_escape(self, html):
        return handle().escape(html)
    
    def mark_safe(self, html):
        return handle().mark_safe(html)
    
    def render_to_string(self, template_name, dictionary=None, context_instance=None):
        return handle().render_to_string(template_name,
                                         dictionary=dictionary,
                                         context_instance=context_instance)
    

class LibraryTemplateHandler(BaseTemplateHandler):
    template_class = None
    context_class = None
    
    def __init__(self, config):
        self.config = config
        self.setup()
    
    
_handlers = {}
