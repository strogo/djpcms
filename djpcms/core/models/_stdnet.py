from stdnet.orm import StdNetType

from .base import ModelTypeWrapper


class ModelType(ModelTypeWrapper):
    '''Wrapper for stdnet models.'''
    def setup(self):
        self.meta = self.model._meta
        appmodel = self.appmodel
        self.module_name = self.meta.name
        self.app_label   = self.meta.app_label
        
    def get_view_permission(self):
        return '%s_view' % self.meta.basekey()
    
    def get_add_permission(self):
        return '%s_add' % self.meta.basekey()
    
    def get_change_permission(self):
        return '%s_change' % self.meta.basekey()
    
    def get_delete_permission(self):
        return '%s_delete' % self.meta.basekey()
    
    def _label_for_field(self, name):
        return name
    
    def test(self, model):
        if not isinstance(model,StdNetType):
            raise ValueError
        
    def _getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if callable(attr):
            return attr()
        else:
            return attr
    