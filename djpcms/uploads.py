'''
Image upload function
'''
import os

from djpcms import sites

from django.utils.functional import LazyObject
from django.core.files.storage import get_storage_class

from djpcms.utils import safepath
from djpcms.utils.importer import module_attribute


def _default_uploads(obj, name, model):
    '''
    Default UPLOAD FUNCTIONS
    '''
    return os.path.join(model,name)


class uploader(object):
    
    def __init__(self, model):
        self.model = model.lower()
        self._func = None
    
    def __call__(self, obj, name):
        if not self._func:
            model = self.model.upper()
            sname =  getattr(sites.settings,'ULOADER_FUNCTION_{0}'.format(model),None)
            if sname:
                func = module_attribute(sname,_default_uploads)
            else:
                func = _default_uploads
            self._func = func
        return self._func(obj,name,self.model)
    
    
class storage_manager(LazyObject):
    '''Lazy class for setting flowitem storge'''
    def __init__(self, model):
        self.__dict__['model'] = model
        super(storage_manager,self).__init__()
        
    def _setup(self):
        model = self.model.upper()
        SETMOD = 'STORAGE_MANAGER_{0}'.format(model)
        self._wrapped = get_storage_class(getattr(sites.settings,SETMOD,None))()
        


        