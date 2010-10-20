from datetime import date, datetime

from django.utils.dateformat import format as date_format, time_format

from djpcms.conf import settings
from djpcms.utils import mark_safe 

BOOLEAN_MAPPING = {True: 'yes', False: 'no'}
EMPTY_VALUE = settings.DJPCMS_EMPTY_VALUE


def _boolean_icon(val):
    v = BOOLEAN_MAPPING.get(val,'unknown')
    return mark_safe(u'<span class="%s-bool" alt="%s" />' % (v,v))


def nicerepr(val):
    if isinstance(val,datetime):
        return date_format(val,settings.DATETIME_FORMAT)
    elif isinstance(val,date):
        return date_format(val,settings.DATE_FORMAT)
    elif isinstance(val,bool):
        return _boolean_icon(val)
    else:  
        return val
        

class ModelTypeWrapper(object):
    
    def __init__(self, appmodel):
        self.test(appmodel.model)
        self.appmodel = appmodel
        self.model = appmodel.model
        self.setup()
        
    def test(self, model):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        return name
        
    def appfuncname(self, name):
        return 'extrafunction__%s' % name
    
    def get_value(self, instance, name, default = EMPTY_VALUE):
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(self.request, instance)
        else:
            return default
    
    def label_for_field(self, name):
        '''Get the lable for field or attribute or function *name*.'''
        try:
            return self._label_for_field(name)
        except:
            if self.appmodel:
                func = getattr(self.appmodel,self.appfuncname(name),None)
                if func:
                    return name
            raise AttributeError("Attribute %s not available" % name)
        
    def getrepr(self, name, instance):
        '''representation of field *name* for *instance*.'''
        return nicerepr(self._getrepr(name,instance))
    
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
    
