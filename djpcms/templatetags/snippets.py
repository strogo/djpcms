from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def object_tags(cl):
    if cl.object:
        try:
            tags = cl.object.tags
        except Exception, e:
            return str(e)
    else:
        return u'View does not contain an object'
