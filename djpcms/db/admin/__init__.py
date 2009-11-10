from sites import dbsite
from options import *

def autodiscover():
    """
    Auto-discover along the lines of django.contrib.admin
    """
    import imp
    from django.conf import settings
    filename = 'dbadmin'

    # For each app, we need to look for an dbadmin.py inside that app's
    # package.
    for app in settings.INSTALLED_APPS:
        # Step 1: find out the app's __path__ 
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's admin.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # its admin.py doesn't exist
        try:
            imp.find_module(filename, app_path)
        except ImportError:
            continue

        # Step 3: import the app's admin file. If this has errors we want them
        # to bubble up.
        __import__("%s.%s" % (app,filename))
