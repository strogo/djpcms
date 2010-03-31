from django.contrib.admin import site
from django.contrib.admin.util import label_for_field

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
            