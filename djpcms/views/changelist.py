from djpcms.views import appsite
from django.contrib.admin import site


class ChangeList(object):
    
    def __init__(self, model):
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
        pass