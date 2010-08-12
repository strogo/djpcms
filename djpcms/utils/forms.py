

def add_extra_fields(form, name, field):
    '''
    form must be a form class, not an object
    '''
    from django import forms
    fields = form.base_fields
    if name not in fields:
        fields[name] = field
    return form


def add_hidden_field(form, name, required = False):
    from django import forms
    return add_extra_fields(form,name,forms.CharField(widget=forms.HiddenInput, required = required))

