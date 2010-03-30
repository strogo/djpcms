from django.contrib.admin import site


class ChangeList(object):
    
    def __init__(self, djp):
        self.appsite = appsite
        self.list_display = self.appsite.list_display
        self.model_admin  = site._register.get(appsite.model,None)
        if self.list_display == [] and self.model_admin:
            self.list_display = self.model_admin.list_display
    
    def get_value(self, label, instance):
        fun = getattr(self.appmodel,'extrafunction__%s' % label,None)
        if fun:
            return fun(self.djp, instance)
        else:
            return None