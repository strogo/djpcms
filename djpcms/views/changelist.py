from django.utils.html import escape, conditional_escape

from djpcms.template import loader
from djpcms.core.models import getmodel, nicerepr
from djpcms.utils import force_unicode, smart_str, mark_safe, smart_unicode
from djpcms.views import appsite


class ChangeList(object):
    
    def __init__(self, model, request):
        self.request = request
        self.model = model
    
    def get_value(self, label, instance):
        fun = getattr(self.appmodel,'extrafunction__%s' % label,None)
        if fun:
            return fun(self.djp, instance)
        else:
            return None
        
    def appfuncname(self, name):
        return 'extrafunction__%s' % name            


def nice_items(items):
    for item in items:
        yield nicerepr(item)


def table(headers, queryset_or_list, djp, model = None):
    if not model:
        try:
            model = queryset_or_list.model
        except AttributeError:
            pass
    try:
        cl = model.opts
        return queryset_table(queryset_or_list, djp, model)
    except Exception, e:
        return {'labels':headers,
                'items':(nice_items(items) for items in queryset_or_list)}
        
    
def queryset_table(queryset, djp, appmodel):
    request = djp.request
    cl = appmodel.opts
    if not cl.appmodel or not cl.list_display:
        return ''
    labels = []
    items  = []
    for name in cl.list_display:
        labels.append(cl.label_for_field(name))
    for result in queryset:
        first = True
        id    = ('%s-%s') % (cl.module_name,result.id)
        display = []
        items.append({'id':id,'display':display})
        for field_name in cl.list_display:
            result_repr = cl.getrepr(field_name, result)
            if force_unicode(result_repr) == '':
                result_repr = mark_safe('&nbsp;')
            if (first and not cl.list_display_links) or field_name in cl.list_display_links:
                first = False
                url = cl.url_for_result(request, result)
            else:
                url = None
            
            if url:
                var = mark_safe(u'<a href="%s">%s</a>' % (url, conditional_escape(result_repr)))
            else:
                var = conditional_escape(result_repr)
            display.append(var)
    return {'labels':labels,
            'items':items}

