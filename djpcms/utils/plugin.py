import os
import glob
import logging

from django.utils.text import capfirst
from djpcms.utils import UnicodeObject, force_unicode            

def expand_star(mod_name):
    """
    Expand something like 'djpcms.plugins.*' into a list of all the modules
    there.
    """
    expanded = []
    mod_dir = os.path.dirname(__import__(mod_name[:-2], {}, {}, ['']).__file__)
    for f in glob.glob1(mod_dir, "[!_]*.py"):
        expanded.append('%s.%s' % (mod_name[:-2], f[:-3]))
    return expanded

def loadobjects(plist, BaseClass):
    '''
    Load plugins into cache.
    Called by djpcms.urls
    '''
    metaclass = BaseClass.__metaclass__
    for plugin in plist:
        if plugin.endswith('.*'):
            to_load = expand_star(plugin)
        else:
            to_load = [plugin]
        for p in to_load:
            try:
                mod = __import__(p, '', '', [''])
            except ImportError, e:
                pass
            else:
                for name in dir(mod):
                    kclass = getattr(mod, name)
                    if isinstance(kclass,metaclass) and not kclass.virtual:
                        if not getattr(kclass,'auto_register',True):
                            kclass().register()



class content_tuple(object):
    '''
    Return a tuple of 2 elements tuples. Used in form choice field
    '''
    storage = None
    def __iter__(self):
        def cmp(x,y):
            if x.description > y.description:
                return 1
            else:
                return -1
        ordered = self.storage.values().sort(cmp)
        for c in ordered:
            yield (c.name,c.description)
            
