from djpcms.conf import settings


class ModelWrapper(object):
    
    def __init__(self, appmodel):
        self.test(appmodel.model)
        self.appmodel = appmodel
        self.model = appmodel.model
        self.setup()
        
    def test(self, model):
        raise NotImplementedError
    
    def _label_for_field(self, name):
        raise NotImplementedError
        
    def appfuncname(self, name):
        return 'extrafunction__%s' % name
    
    def get_value(self, instance, name, default = settings.DJPCMS_EMPTY_VALUE):
        func = getattr(self.appmodel,self.appfuncname(name),None)
        if func:
            return func(self.request, instance)
        else:
            return default
    
    def label_for_field(self, name):
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
        raise NotImplementedError
    
    def url_for_result(self, request, instance):
        if self.appmodel:
            return self.appmodel.viewurl(request, instance)
        else:
            return None
        
    def has_add_permission(self, request = None, obj=None):
        return False
    
    def has_edit_permission(self, request = None, obj=None):
        return False
    
    def has_view_permission(self, request = None, obj = None):
        return True
    
    def has_delete_permission(self, request = None, obj=None):
        return False
    
