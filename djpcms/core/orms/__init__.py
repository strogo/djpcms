from djpcms import sites
from djpcms.core.exceptions import ModelException
from djpcms.utils.py2py3 import itervalues
 
from .base import *
from .user import monkey_patch_user

sites.register_orm('django')
sites.register_orm('stdnet')


def getmodel(appmodel):
    global _models
    for wrapper in _models.itervalues():
        try:
            return wrapper(appmodel)
        except:
            continue
    raise ModelException('Model {0} not recognised'.format(appmodel))
def mapper(model):
    '''Return an instance of a ORM djpcms wrapper'''
    if not isinstance(model,type):
        instance = model
        model = instance.__class__
    wrapper = getattr(model,'_djpcms_orm_wrapper',None)
    if not wrapper:
        for wrapper in itervalues(sites.modelwrappers):
            try:
                wrapper = wrapper(model)
                break
            except ValueError:
                continue
        if not wrapper:
            raise AttributeError
        else:
            setattr(model,'_djpcms_orm_wrapper',wrapper)
    return wrapper
    
    
def getid(obj):
    '''If ``obj`` is an instance of a ORM it returns its id'''
    if obj:
        try:
            return obj.id
        except AttributeError, SyntaxError:
            return obj
    else:
        return obj
        
