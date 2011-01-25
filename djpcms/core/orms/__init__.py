from djpcms.core.exceptions import ModelException
 
from .base import *

_models = {}
_modelwrappers = {}

try:
    from ._django import ModelType, OrmWrapper
    _modelwrappers['django'] = OrmWrapper
    _models['django'] = ModelType
except:
    pass

try:
    from ._stdnet import ModelType, OrmWrapper
    _modelwrappers['stdnet'] = OrmWrapper
    _models['stdnet'] = ModelType
except:
    pass


def register(name,wrapper):
    _models[name] = wrapper


def getmodel(appmodel):
    global _models
    for wrapper in _models.itervalues():
        try:
            return wrapper(appmodel)
        except:
            continue
    raise ModelException('Model {0} not recognised'.format(appmodel))


def orm_wrapper(model):
    for wrapper in _modelwrappers.itervalues():
        try:
            return wrapper(model)
        except:
            continue
        
        
class orm_method(object):
    
    def __init__(self, name):
        self.method_name = name
    
    def __call__(self, model, *args, **kwargs):
        if not isinstance(model,type):
            instance = model
            model = instance.__class__
        wrapper = getattr(model,'_djpcms_orm_wrapper',None)
        if not wrapper:
            wrapper = orm_wrapper(model)
            if not wrapper:
                raise AttributeError
            else:
                setattr(model,'_djpcms_orm_wrapper',wrapper)
        return getattr(wrapper,self.method_name)(model, *args, **kwargs)

        
            
model_to_dict = orm_method('model_to_dict')
        
