#
# Load the markup module
# This hook is provided so that third-party markup libraries
# can be used rather than the limited one in djpcms
#

class MarkupLib(object):
    
    def __init__(self):
        self._module = None
        
    @property
    def markup_module(self):
        if not self._module:
            from djpcms.conf import settings
            self._module = __import__(settings.DJPCMS_MARKUP_MODULE,globals(),locals(),[''])
        return self._module

    def choices(self):
        return self.markup_module.choices()
     
    def default(self):
        # default markup, a string
        return self.markup_module.default

    def get(self, code):
        # get method to obtain the markup handler
        return self.markup_module.get(code)

markuplib = MarkupLib()