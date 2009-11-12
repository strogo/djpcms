
from djpcms.utils.markups import creole


class MarkupMacro(object):
    '''
    Base class for markup macros
    '''
    code        = None
    description = None
    usage       = None
    
    def __init__(self):
        if not self.code:
            self.code = self.__class__.__name__
    
    def __call__(self, *args, **kwargs):
        '''
        Macros must implements this functions
        '''
        return u''
    
    
def _addmacro(macro, MacroHolder):
    if not isinstance(macro, MarkupMacro):
        return
    if not MacroHolder.has_key(name):
        MarkupMacro[name] = func
        


def addCreoleMacro(macro):
    _addmacro(macro,creole.MACRO_HOLDER)