import os

from django.core.files.storage import FileSystemStorage
from django.core.files.storage import get_storage_class
from django.utils.importlib import import_module
from django.utils._os import safe_join

from django.conf import settings


class pathHandler(object):
    def __init__(self, name, path):
        self.name     = name
        self.base     = path
        self._path    = os.path.join(path,'media')
        self.fullpath = self.path(name)
        self.exists   = os.path.exists(self._path)
    
    def path(self, name):
        return safe_join(self._path, name)

class djangoAdminHandler(pathHandler):
    def path(self, name):
        name = (name.split('/')[1:])
        return safe_join(self._path, *name)


def application_map():
    map = {}
    for app in settings.INSTALLED_APPS:
        sapp = app.split('.')
        name = sapp[-1]
        if app.startswith('django.'):
            if app == 'django.contrib.admin':
                base = settings.ADMIN_MEDIA_PREFIX[1:-1].split('/')[-1]
                handler = djangoAdminHandler
            else:
                continue
        else:
            base    = name
            handler = pathHandler
            
        try:
            module = import_module(app)
        except:
            continue

        path   = module.__path__[0]
        map[base] = handler(name,path)
    return map


class CompressorFileStorage(FileSystemStorage):
    """
    Standard file system storage for files handled by django-compressor.

    The defaults for ``location`` and ``base_url`` are ``COMPRESS_ROOT`` and
    ``COMPRESS_URL``.

    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.MEDIA_ROOT
        if base_url is None:
            base_url = settings.MEDIA_URL
        self.map = application_map()
        super(CompressorFileStorage, self).__init__(location, base_url,
                                                    *args, **kwargs)
        
    def path(self, name):
        sp = False
        try:
            path = safe_join(self.location, name)
        except ValueError:
            sp = True
        if not sp:
            bpath = os.path.normpath(path)
            if os.path.exists(bpath):
                return bpath
            
        app     = name.split('/')[0]
        handler = self.map.get(app,None)
        if handler:
            try:
                path = handler.path(name)
            except:
                sp = True
            return os.path.normpath(path)
        
        if sp:
            raise FileSystemStorage.SuspiciousOperation("Attempted access to '%s' denied." % name)
        else:
            return bpath

