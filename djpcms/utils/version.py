_versions = {}

import copy
import sys
from django.utils.importlib import import_module
from django.conf import settings

from djpcms.utils import appurls

def get():
    return copy.copy(_versions)

def addversion(name,v):
    global _versions
    if not _versions.has_key(name):
        _versions[name] = {'name': name,
                           'version': u'%s' % v,
                           'url': appurls.urls.get(name,None)}

def flatattr(vt, N = 3):
    try:
        av = []
        for v in vt[0:N]:
            av.append(str(v))
        return '.'.join(av)
    except:
        return str(vt)

import django
addversion('python',flatattr(sys.version_info))
addversion('django',django.get_version())


def cleanversion(v, N = 3):
    if isinstance(v,str) or isinstance(v,unicode):
        return v
    else:
        return flatattr(v,N)

# Check for application versions
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        try:
            module = import_module(app)
        except:
            continue
        try:
            v = module.VERSION
        except:
            try:
                v = module.__version__
            except:
                try:
                    v = module.get_version()
                except:
                    continue
        addversion('django-%s' % app,cleanversion(v))


