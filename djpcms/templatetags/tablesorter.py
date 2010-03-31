from django import template
from django.db import models
from django.contrib.admin import site
from django.contrib.admin.util import label_for_field, display_for_field, lookup_field
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape, conditional_escape
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from djpcms.utils import force_unicode, smart_str, mark_safe, smart_unicode
from djpcms.views.changelist import ChangeList

EMPTY_VALUE = '(None)'

register = template.Library()

@register.inclusion_tag('djpcms/tablesorter.html')
def totable(queryset, djp):
    request = djp.request
    cl    = ChangeList(queryset.model, request)
    if not cl.list_display:
        return ''
    labels = []
    items  = []
    for name in cl.list_display:
        labels.append(cl.label_for_field(name))
    first = True
    #pk = cl.lookup_opts.pk.attname
    for result in queryset:
        display = []
        items.append(display)
        for field_name in cl.list_display:
            row_class = ''
            try:
                f, attr, value = lookup_field(field_name, result, cl.model_admin)
            except (AttributeError, ObjectDoesNotExist):
                result_repr = cl.get_value(result, field_name, EMPTY_VALUE)
            else:
                if f is None:
                    allow_tags = getattr(attr, 'allow_tags', False)
                    boolean = getattr(attr, 'boolean', False)
                    if boolean:
                        allow_tags = True
                        result_repr = _boolean_icon(value)
                    else:
                        result_repr = smart_unicode(value)
                    # Strip HTML tags in the resulting text, except if the
                    # function has an "allow_tags" attribute set to True.
                    if not allow_tags:
                        result_repr = escape(result_repr)
                    else:
                        result_repr = mark_safe(result_repr)
                else:
                    if value is None:
                        result_repr = EMPTY_VALUE
                    if isinstance(f.rel, models.ManyToOneRel):
                        result_repr = escape(getattr(result, f.name))
                    else:
                        result_repr = display_for_field(value, f)
                    if isinstance(f, models.DateField) or isinstance(f, models.TimeField):
                        row_class = ' class="nowrap"'
            if force_unicode(result_repr) == '':
                result_repr = mark_safe('&nbsp;')
            # If list_display_links not defined, add the link tag to the first field
            if (first and not cl.list_display_links) or field_name in cl.list_display_links:
                first = False
                url = cl.url_for_result(result)
            else:
                url = None
            
            if url:
                var = mark_safe(u'<a href="%s">%s</a>' % (url, conditional_escape(result_repr)))
            else:
                var = conditional_escape(result_repr)
            display.append(var)
    return {'labels':labels,
            'items':items}
    
    
    
    