import json
from .base import handle, BaseTemplateHandler

loader = BaseTemplateHandler()

# Default Implementation
mark_safe = loader.mark_safe
escape = loader.escape
conditional_escape = loader.conditional_escape
#Template = loader.template_class
#Context = loader.context_class
#RequestContext = loader.request_context
json_dump_safe = lambda data: loader.mark_safe(json.dumps(data))
