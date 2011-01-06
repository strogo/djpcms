import json
from djpcms import sites


def handle(engine = None):
    engine = engine or sites.settings.TEMPLATE_ENGINE
    handle = _handlers.get(engine,None)
    if not handle:
        handle = get_engine(engine)
        _handlers[engine] = handle
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


_handlers = {}


# Default Implementation
loader = handle()
mark_safe = loader.mark_safe
escape = loader.escape
conditional_escape = loader.conditional_escape
Template = loader.template_class
Context = loader.context_class
RequestContext = loader.request_context
json_dump_safe = lambda data: mark_safe(json.dumps(data))

    