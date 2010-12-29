


class BaseTemplateHandler(object):
    context_class = None
    
    def __init__(self, config):
        self.config = config
        self.setup()
        
    def setup(self):
        raise NotImplementedError
    
    def get_processors(self):
        return []
    
    def request_context(self, request, dict=None, processors=None, current_app=None):
        c = self.context_class(dict, current_app=current_app, autoescape=True)
        if processors is None:
            processors = ()
        else:
            processors = tuple(processors)
        for processor in self.get_processors() + processors:
            c.update(processor(request))
        return c