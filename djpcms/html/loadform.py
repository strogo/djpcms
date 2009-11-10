from django import forms

from form import form, formlet, submit

__all__ = ['LoadForm','simpleloadform']

class LoadForm(forms.Form):
    file = forms.FileField()
    
    
class simpleloadform(form):
    
    def __init__(self, namefun = 'load_file', *args, **kwargs):
        self.name_fun = namefun
        super(simpleloadform,self).__init__(*args, **kwargs)
    
    def _make(self, data = None, files = None, *args, **kwargs):
        self.attrs['enctype'] = "multipart/form-data"
        co = self.make_container()
        co['loadform'] = formlet(form   = LoadForm,
                                 data   = data,
                                 files  = files,
                                 submit = submit(value = 'Load', name = self.name_fun))
