

class MarkupLib(object):
    '''Load the markup module. This hook is provided so that third-party markup libraries
can be used rather than the limited one in djpcms'''

    def __init__(self):
        self._module = None
        
    @property
    def markup_module(self):
        from djpcms.contrib.flowrepo import markups
        return markups

    def choices(self):
        return self.markup_module.choices()
     
    def default(self):
        # default markup, a string
        return self.markup_module.default

    def get(self, code):
        # get method to obtain the markup handler
        return self.markup_module.get(code)

markuplib = MarkupLib()