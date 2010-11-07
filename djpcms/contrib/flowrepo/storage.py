import datetime
from django.utils.functional import LazyObject
from django.core.files.storage import Storage, get_storage_class

def uploader(obj, name):
    '''
    Upload object
    '''
    from flowrepo import settings 
    if settings.FLOWREPO_UPLOAD_FUNCTION:
        bits = settings.FLOWREPO_UPLOAD_FUNCTION.split('.')
        module = __import__('.'.join(bits[:-1]),globals(),locals(),[''])
        func = getattr(module,bits[-1],None)
        return func(obj,name)
    else:
        # default
        # The slug field is unique. Name the file with it
        extension = name.split('.')[-1].lower()
        return 'flowrepo/%s/%s.%s' % (obj.__class__.__name__.lower(),obj.slug,extension)
    
    
class storage_manager(LazyObject):
    '''Lazy class for setting flowitem storge'''
    def __init__(self, model):
        self.__dict__['model'] = model
        super(storage_manager,self).__init__()
        
    def _setup(self):
        from flowrepo import settings
        SETMOD = 'FLOWREPO_STORAGE_%s' % self.model
        self._wrapped = get_storage_class(getattr(settings,SETMOD,None))()
        
