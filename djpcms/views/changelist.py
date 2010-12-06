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


def nice_items(items,nd):
    for item in items:
        yield nicerepr(item,nd)
        


def table(headers, queryset_or_list, djp, model = None, nd = 3):
    if not model:
        try:
            model = queryset_or_list.model
        except AttributeError:
            pass
    try:
        cl = model.opts
        return queryset_table(headers, queryset_or_list, djp, model, nd)
    except Exception, e:
        return {'labels':headers,
                'items':(nice_items(items,nd) for items in queryset_or_list)}
        
    
def queryset_table(headers, queryset, djp, appmodel, nd):
    request = djp.request
    cl = appmodel.opts
    headers = headers or cl.list_display
    if not cl.appmodel or not headers:
        return ''
    labels = []
    items  = []
    path   = djp.request.path
    for name in headers:
        labels.append(cl.label_for_field(name))
    for result in queryset:
        first = True
        id    = ('%s-%s') % (cl.module_name,result.id)
        display = []
        items.append({'id':id,'display':display})
        for field_name in headers:
            result_repr = cl.getrepr(field_name, result, nd)
            if force_unicode(result_repr) == '':
                result_repr = mark_safe('&nbsp;')
            if (first and not cl.list_display_links) or field_name in cl.list_display_links:
                first = False
                url = cl.url_for_result(request, result)
            else:
                url = None
            
            if url and url != path:
                var = mark_safe(u'<a href="%s">%s</a>' % (url, conditional_escape(result_repr)))
            else:
                var = conditional_escape(result_repr)
            display.append(var)
    return {'labels':labels,
            'items':items}

