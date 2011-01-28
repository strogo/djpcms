from .forms import UniForm


__all__ = ['def_form_data']


class def_form_data(object):
    '''Decorator for filling a data dictionary with form default values.
Useful for testing.'''
    def __init__(self, formcls):
        self.formcls = formcls
        self.factory = lambda *args, **kwargs : UniForm(self.formcls(*args, **kwargs))
        
    def data(self, data = None):
        d = self.factory().htmldata()
        if data:
            d.update(data)
        return d
        
    def __call__(self, f):
        def wrapper(*args, **kwargs):
            return self.data(f(*args, **kwargs))
        return wrapper
        
