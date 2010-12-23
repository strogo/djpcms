import json
from djpcms.conf import settings

if settings.TEMPLATE_ENGINE == 'django':
    from ._django import *
elif settings.TEMPLATE_ENGINE == 'jinja2':
    from ._jinja2 import *
elif settings.TEMPLATE_ENGINE == 'cheetah':
    raise NotImplementedError("Cheetah not yet supported. Coming soon.")
elif settings.TEMPLATE_ENGINE == 'mustache':
    raise NotImplementedError("mustache not yet supported. Coming soon.")
else:
    raise NotImplementedError("...")


json_dump_safe = lambda data: mark_safe(json.dumps(data))

    