
__all__ = ['register_plugin',
           'get_plugin',
           'all_plugins',
           'Options']

class PlugIns(object):

    def __init__(self):
        self._plugins = {}
        
    def register(self, *models):
        plugs = self._plugins
        for model in models:
            #name = model._meta.name.lower()
            name = model._meta.name
            plugs[name] = model
            
    def get(self, name):
        '''
        Return a plugin class if available.
        Otherwise return None
        '''
        return self._plugins.get(name.lower())
    
    def all(self):
        return self._plugins.keys()


class Options(object):
    
    def __init__(self, meta):
        self.abstract = False
        self.name     = None
        self.meta     = meta
        
    def contribute_to_class(self, cls, name):
        cls._meta = self
        self.name = cls.__name__
        
        if self.meta:
            self.abstract = self.meta.abstract
        del self.meta


cache = PlugIns()

register_plugin = cache.register
get_plugin      = cache.get
all_plugins     = cache.all