from djpcms.conf import settings

if settings.TEMPLATE_ENGINE == 'django':
    from django.template import *
    from django.template import loader
elif settings.TEMPLATE_ENGINE == 'cheetah':
    raise NotImplementedError("Cheetah not yet supported. Coming soon.")
elif settings.TEMPLATE_ENGINE == 'mustache':
    raise NotImplementedError("mustache not yet supported. Coming soon.")
else:
    raise NotImplementedError("...")
    