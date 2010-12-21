from djpcms.core.exceptions import ModelException 
from base import *

_models = {}

try:
    from djpcms.core.models import _django
    _models['django'] = _django.ModelType
except:
    pass

try:
    from djpcms.core.models import _stdnet
    _models['stdnet'] = _stdnet.ModelType
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
    raise ModelException('Model not recognised')
