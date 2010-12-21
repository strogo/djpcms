from datetime import date, datetime

from django.utils.dateformat import format as date_format, time_format

from djpcms.conf import settings
from djpcms.utils import mark_safe, force_unicode, significant_format
from djpcms.utils import escape, conditional_escape
from djpcms.template import loader



__all__ = ['ModelTypeWrapper',
           'nicerepr',
           '_boolean_icon',
           'nicerepr',
           'table']
 

BOOLEAN_MAPPING = {True: {'icon':'ui-icon-check','name':'yes'},
                   False: {'icon':'ui-icon-close','name':'no'}}
EMPTY_VALUE = settings.DJPCMS_EMPTY_VALUE


def _boolean_icon(val):
    v = BOOLEAN_MAPPING.get(val,'unknown')
    return mark_safe(u'<span class="ui-icon %(icon)s" title="%(name)s">%(name)s</span>' % v)


def nicerepr(val, nd = 3):
    if isinstance(val,datetime):
        time = val.time()
        if not time:
            return date_format(val.date(),settings.DATE_FORMAT)
        else:
            return date_format(val,settings.DATETIME_FORMAT)
    elif isinstance(val,date):
        return date_format(val,settings.DATE_FORMAT)
    elif isinstance(val,bool):
        return _boolean_icon(val)
    else:
        try:
            return significant_format(val, n = nd)
        except:
            return val



def nice_items_id(items, id = None, nd = 3):
    return {'id': id,
            'display': (nicerepr(c,nd) for c in items)}


def table(headers, queryset_or_list, djp, model = None, nd = 3):
    '''Render a table'''
    if not model:
        try:
            model = queryset_or_list.model
        except AttributeError:
            pass
    cl = getattr(model,'opts',None)
    if not cl:
        labels = headers
        items  = (nice_items_id(items,nd=nd) for items in queryset_or_list)
    else:
        labels = (cl.label_for_field(name) for name in headers)
        items  = (cl.result_for_item(headers, items, djp, nd) for items in queryset_or_list)
    
    return {'labels': labels,
            'items': items}
        

class ModelTypeWrapper(object):
    '''Base class for wrapping Object Relational Mapping models'''
    def __init__(self, appmodel):
        self.list_display = appmodel.list_display or []
        self.object_display = appmodel.object_display or self.list_display
        self.list_display_links = appmodel.list_display_links or []
        self.search_fields = appmodel.search_fields or []
        self.test(appmodel.model)
        self.appmodel = appmodel
        self.model = appmodel.model
        self.setup()
        
    def test(self, model):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        return name
        
    def appfuncname(self, name):
        return 'objectfunction__%s' % name
    
    def get_value(self, instance, name, default = EMPTY_VALUE):
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(instance)
        else:
            return default
    
    def label_for_field(self, name):
        '''Get the lable for field or attribute or function *name*.'''
        try:
            return self._label_for_field(name)
        except:
            pass
        try:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return func(name)
                else:
                    return self.appmodel.get_label_for_field(name)
        except:
            return name
        
    def result_for_item(self, headers, result, djp, nd = 3):
        if isinstance(result, self.model):
            request = djp.request
            path  = request.path
            first = True
            id    = ('%s-%s') % (self.module_name,result.id)
            display = []
            item = {'id':id,'display':display}
            for field_name in headers:
                result_repr = self.getrepr(field_name, result, nd)
                if force_unicode(result_repr) == '':
                    result_repr = mark_safe('&nbsp;')
                if (first and not self.list_display_links) or field_name in self.list_display_links:
                    first = False
                    url = self.url_for_result(request, result)
                else:
                    url = None
                
                if url and url != path:
                    var = mark_safe(u'<a href="%s">%s</a>' % (url, conditional_escape(result_repr)))
                else:
                    var = conditional_escape(result_repr)
                display.append(var)
            return item
        else:
            return nice_items_id(result, nd = nd)
        
    def getrepr(self, name, instance, nd = 3):
        '''representation of field *name* for *instance*.'''
        return nicerepr(self._getrepr(name,instance),nd)
    
    def _getrepr(self, name, instance):
        raise NotImplementedError
    
    def url_for_result(self, request, instance):
        if self.appmodel:
            return self.appmodel.viewurl(request, instance)
        else:
            return None
        
    def has_add_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_change_permission(self, user, obj=None):
        return user.is_superuser
    
    def has_view_permission(self, user, obj = None):
        return True
    
    def has_delete_permission(self, user, obj=None):
        return user.is_superuser
    
    def get_object_id(self, obj):
        return '%s-%s' % (self.module_name,obj.id)
    
    def totable(self, obj):
        '''Render an object as definition list.'''
        label_for_field = self.label_for_field
        getrepr = self.getrepr
        def data():
            for field in self.object_display:
                name = label_for_field(field)
                yield {'name':name,'value':getrepr(field,obj)}
        content = {'module_name':self.module_name,
                   'id':self.get_object_id(obj),
                   'data':data(),
                   'item':obj}
        return loader.render_to_string(['%s/%s_table.html' % (self.app_label,self.module_name),
                                        'djpcms/components/object_definition.html'],
                                        content)
            
    def model_to_dict(self, instance, fields = None, exclude = None):
        raise NotImplementedError
        
