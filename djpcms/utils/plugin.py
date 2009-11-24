import os
import glob
import logging

from djpcms.utils import UnicodeObject

log = logging.getLogger("djpcms.utils.plugins")


class PluginBase(UnicodeObject):
    virtual       = False
    name          = None
    description   = None
    storage       = None
        
    def __unicode__(self):
        return self.description
    
    def register(self):
        if self.name is None:
            return self
        storage = self.storage
        if not storage.has_key(self.name):
            self.description = self.description or self.name
            storage[self.name] = self
        return self
            

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
                log.error("Couldn't import provider %r: %s" % (p, e))
            else:
                for name in dir(mod):
                    kclass = getattr(mod, name)
                    if isinstance(kclass,metaclass) and not kclass == BaseClass and not kclass.virtual:
                        kclass().register()



class content_tuple(object):
    '''
    Return a tuple of 2 elements tuples. Used in form choice field
    '''
    storage = None
    def __iter__(self):
        for c in self.storage.values():
            yield (c.name,c.description)
            
