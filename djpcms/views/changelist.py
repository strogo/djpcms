from django.db import models
from django.contrib.admin import site
from django.contrib.admin.util import label_for_field, display_for_field, lookup_field
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import escape, conditional_escape
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from djpcms.template import loader
from djpcms.utils import force_unicode, smart_str, mark_safe, smart_unicode
from djpcms.views import appsite


EMPTY_VALUE = '(None)'

class ChangeList(object):
    
    def __init__(self, model, request):
        self.request = request
        appmodel = appsite.site.for_model(model)
        model_admin  = site._registry.get(model,None)
        self.appmodel = appmodel
        self.model_admin = model_admin
        self.model = model
        if appmodel:
            list_display = appmodel.list_display
            list_display_links = appmodel.list_display_links
            if list_display is None:
                if model_admin:
                    list_display = model_admin.list_display
                else:
                    list_display = []
            if list_display_links is None:
                if model_admin:
                    list_display_links = model_admin.list_display_links
                else:
                    list_display_links = []
        elif model_admin:
            list_display = model_admin.list_display
            list_display_links = model_admin.list_display_links
        self.list_display = list_display
        self.list_display_links = list_display_links
    
    def get_value(self, label, instance):
        fun = getattr(self.appmodel,'extrafunction__%s' % label,None)
        if fun:
            return fun(self.djp, instance)
        else:
            return None
        
    def url_for_result(self, instance):
        if self.appmodel:
            return self.appmodel.viewurl(self.request, instance)
        else:
            return None
        
    def appfuncname(self, name):
        return 'extrafunction__%s' % name
    
    def get_value(self, instance, name, default = EMPTY_VALUE):
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(self.request, instance)
        else:
            return default
    
    def label_for_field(self, name):
        try:
            return label_for_field(name, self.model, self.model_admin)
        except:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return name
            raise AttributeError("Attribute %s not available" % name)
            


def table(queryset, djp, model = None):
    try:
        queryset.model
    except AttributeError:
        return dict_table(queryset, djp, model = model)
    else:
        return queryset_table(queryset, djp, model = model)
    

def dict_table(data, djp, model = None):
    return data    
    
def queryset_table(queryset, djp, model = None):
    model = model or queryset.model
    request = djp.request
    cl      = ChangeList(model, request)
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



