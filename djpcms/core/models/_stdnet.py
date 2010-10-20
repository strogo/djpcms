from stdnet.orm import DataMetaClass

from base import ModelWrapper

class Model(ModelWrapper):
    '''Wrapper for stdnet models.'''
    def setup(self):
        self.meta = self.model._meta
        appmodel = self.appmodel
        self.module_name = self.meta.name
        self.app_label   = self.meta.app_label
        self.list_display = appmodel.list_display
        self.list_display_links = appmodel.list_display_links or []
        
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
        if not isinstance(model,DataMetaClass):
            raise ValueError
        
    def getrepr(self, name, instance):
        attr = getattr(instance,name,None)
        if callable(attr):
            return attr()
        else:
            return attr
    