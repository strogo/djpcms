'''
Image upload function
'''
import os

from django.core.files.storage import FileSystemStorage

from djpcms.djutils.func import function_module, safepath


def _default_uploads(obj, name):
    '''
    Default function for editing permissions
    '''
    path = 'images'
    if obj.path:
        obj.path = safepath(obj.path)
        if obj.path:
            path = os.path.join(path,obj.path)
    return os.path.join(path,name)



def upload_function(obj, name):
    from djpcms.settings import DJPCMS_IMAGE_UPLOAD_FUNCTION
    if DJPCMS_IMAGE_UPLOAD_FUNCTION:
        func = function_module(DJPCMS_IMAGE_UPLOAD_FUNCTION,_default_uploads)
        try:
            return func(obj, name)
        except:
            return _default_uploads(obj, name)
    else:
        return _default_uploads(obj, name)
    
    
    
def site_image_storage():
    return FileSystemStorage()