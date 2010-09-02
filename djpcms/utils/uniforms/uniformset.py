from djpcms.utils import form_kwargs, force_unicode

class ModelFormInlineHelper(object):
    '''Inline formset helper for model with foreign keys.'''
    def __init__(self, parent_model, model, legend = None, **kwargs):
        from django.forms.models import inlineformset_factory
        self.parent_model = parent_model
        self.model   = model
        self.legend  = None
        if legend is not False:
            self.legend = legend or force_unicode(model._meta.verbose_name_plural)
        self.FormSet = inlineformset_factory(parent_model, model, **kwargs)
        
    def get_default_prefix(self):
        return self.FormSet.get_default_prefix()
    
    def queryset(self, request):
        return self.model._default_manager.all()
    
    def get_formset(self, request = None, instance = None, prefix = None):
        formset = self.FormSet(**form_kwargs(request  = request,
                                             instance = instance,
                                             prefix   = prefix,
                                             queryset = self.queryset(request)))
        return FormsetWrap(formset)
    

class FormsetWrap(object):
    
    def __init__(self, formset):
        self.formset = formset
        
    def __iter__(self):
        for form in self.formset.forms:
            yield form
            
    def is_valid(self):
        return self.formset.is_valid()
        
    def fields(self):
        formset = self.formset
        fk = getattr(formset, "fk", None)
        for name,field in formset.form.base_fields.items():
            if fk and fk.name == name:
                continue
            yield field

