
from django import forms


def addfield(form, name, field):
    '''
    dynamically add an extra field to a form class
    '''
    form.base_fields[name] = field
    return form
    
def addhiddenfield(form, name, required = True):
    return addfield(form, name, forms.CharField(widget=forms.HiddenInput, required = required))


class FormRequestFactory(object):
    
    def __init__(self, form, request):
        self.form    = form
        self.request = request
    
    def __call__(self, *args, **kwargs):
        kwargs['request'] = self.request
        return self.form(*args, **kwargs)


