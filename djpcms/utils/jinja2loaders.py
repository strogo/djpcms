import os

from djpcms import sites
from djpcms.utils.importer import import_module
from djpcms.core.exceptions import ImproperlyConfigured

from jinja2 import loaders


def application_directories(package_path):
    app_template_dirs = []
    for app in sites.settings.INSTALLED_APPS:
        try:
            mod = import_module(app)
        except ImportError, e:
            raise ImproperlyConfigured('ImportError %s: %s' % (app, e.args[0]))
        template_dir = os.path.join(os.path.dirname(mod.__file__), package_path)
        if os.path.isdir(template_dir):
            app_template_dirs.append(template_dir)
    return app_template_dirs


class FileSystemLoader(loaders.FileSystemLoader):
    
    def __init__(self, searchpath = None, encoding='utf-8'):
        searchpath = searchpath or sites.settings.SITE_DIRECTORY
        super(FileSystemLoader,self).__init__(searchpath,encoding)
        

class ApplicationLoader(loaders.FileSystemLoader):
    
    def __init__(self, package_path='templates', encoding='utf-8'):
        searchpath = application_directories(package_path)
        super(ApplicationLoader,self).__init__(searchpath,encoding)
        