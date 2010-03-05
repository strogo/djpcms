#
# Load the markup module
# This hook is provided so that third-party markup libraries
# can be used rather than the limited one in djpcms
#

class mchoices(object):
    
    def __init__(self, lib):
        self.lib = lib
    
    def __iter__(self):
        return [].__iter__()
    
    def __next__(self):
        c = self.lib.markup_module().choices
        return c.__iter__()

class MarkupLib(object):
    
    def __init__(self):
        self._module = None
        self.choices = mchoices(self)
        
    def markup_module(self):
        if not self._module:
            from djpcms.conf import settings
            self._module = __import__(settings.DJPCMS_MARKUP_MODULE,globals(),locals(),[''])
        return self._module

    def default(self):
        # default markup, a string
        return self.markup_module().default

    def get(self, code):
        # get method to obtain the markup handler
        return self.markup_module().get(code)

markuplib = MarkupLib()