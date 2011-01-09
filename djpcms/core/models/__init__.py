from djpcms.core.exceptions import ModelException
 
from .base import *

_models = {}

try:
    from ._django import ModelType
    _models['django'] = ModelType
except:
    pass

try:
    from ._stdnet import ModelType
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
