from django import template
from django.db import models
from django.contrib.admin import site
from django.contrib.admin.util import label_for_field, display_for_field, lookup_field
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape, conditional_escape

from djpcms.utils import force_unicode, smart_str

EMPTY_VALUE = '(None)'

register = template.Library()

@register.inclusion_tag('djpcms/tablesorter.html')
def totable(queryset, djp):
    request = djp.request
    model = queryset.model
    model_admin = site._registry.get(model,None)
    if not model_admin:
        return ''
    list_display = model_admin.list_display
    labels = []
    items  = []
    for name in list_display:
        labels.append(label_for_field(name, model, model_admin))
    first = True
    #pk = cl.lookup_opts.pk.attname
    for result in queryset:
        display = []
        items.append(display)
        for field_name in list_display:
            row_class = ''
            try:
                f, attr, value = lookup_field(field_name, result, model_admin)
            except (AttributeError, ObjectDoesNotExist):
                result_repr = EMPTY_VALUE
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
                        result_repr = EMPTY_CHANGELIST_VALUE
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
                table_tag = {True:'th', False:'td'}[first]
                first = False
                url = cl.url_for_result(result)
                # Convert the pk to something that can be used in Javascript.
                # Problem cases are long ints (23L) and non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                result_id = repr(force_unicode(value))[1:]
                #yield mark_safe(u'<%s%s><a href="%s"%s>%s</a></%s>' % \
                #                (table_tag, row_class, url, (cl.is_popup and ' onclick="opener.dismissRelatedLookupPopup(window, %s); return false;"' % result_id or ''), conditional_escape(result_repr), table_tag))
            else:
                # By default the fields come from ModelAdmin.list_editable, but if we pull
                # the fields out of the form instead of list_editable custom admins
                # can provide fields on a per request basis
                if form and field_name in form.fields:
                    bf = form[field_name]
                    result_repr = mark_safe(force_unicode(bf.errors) + force_unicode(bf))
                else:
                    result_repr = conditional_escape(result_repr)
                
            display.append({'class':row_class,
                            'result': result_repr})
    return {'labels':labels,
            'items':items}
    
    
    
    