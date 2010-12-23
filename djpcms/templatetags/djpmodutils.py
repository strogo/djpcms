from django import template
from django.db import models

from djpcms.utils import force_str
from djpcms.views import appsite

register = template.Library()

@register.filter
def site_address(request):
    host = request.environ.get('HTTP_HOST','')
    if host:
        if request.is_secure():
            return 'https://%s' % host
        else:
            return 'http://%s' % host
    else:
        return ''
    


@register.filter
def nicefield(model,name):
    opts = model._meta
    try:
        label = force_str(opts.get_field_by_name(name)[0].verbose_name)
    except models.FieldDoesNotExist:
        if name == "__str__":
            label = force_str(opts.verbose_name)
        elif hasattr(model, name):
            attr = getattr(model, name)
        else:
            message = "Unable to lookup '%s' on %s" % (name, opts.object_name)
            raise AttributeError(message)

        if attr:
            if hasattr(attr, "short_description"):
                label = attr.short_description
            elif callable(attr):
                if attr.__name__ == "<lambda>":
                    label = "--"
                else:
                    label = attr.__name__
            else:
                label = name
    return label

        
@register.filter
def objvalue(obj,name):
    opts = obj._meta
    try:
        f = opts.get_field(name)
    except models.FieldDoesNotExist:
        attr = getattr(obj,name,None)
        if attr:
            if callable(attr):
                value = attr()
            else:
                value = attr
        else:
            value = ''
    else:
        value = getattr(obj, name)
    return value
    
    
@register.filter
def objtable(obj):
    appmodel = appsite.site.for_model(obj.__class__)
    if appmodel:
        return appmodel.opts.totable(obj)
    else:
        return obj
    