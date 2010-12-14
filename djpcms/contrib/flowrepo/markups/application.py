


class Application(object):
    code = None
    name = None
    
    def __init__(self):
        from djpcms.contrib.flowrepo import settings
        self.config = settings.MARKUP_CONFIG.get(self.code,{})
        
    def setup(self):
        self.setup_extensions()
        
    def setup_extensions(self):
        for extension in self.config['extensions']:
            self.setup_extension(extension)
            
    def setup_extension(self, extension):
        pass