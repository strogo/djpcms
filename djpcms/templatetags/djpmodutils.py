from django import template
from django.db import models

from djpcms.utils import force_unicode, smart_str

register = template.Library()

@register.filter
def nicefield(model,name):
    opts = model._meta
    try:
        label = force_unicode(opts.get_field_by_name(name)[0].verbose_name)
    except models.FieldDoesNotExist:
        if name == "__unicode__":
            label = force_unicode(opts.verbose_name)
        elif name == "__str__":
            label = smart_str(opts.verbose_name)
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
    