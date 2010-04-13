from django import forms
    

class ModelChoiceField(forms.ModelChoiceField):
    
    def __init__(self, queryset, search_fields, widget = None, **kwargs):
        self.widget = widget or AutocompleteForeignKeyInput(queryset, search_fields)
        super(ModelChoiceField,self).__init__(queryset, **kwargs)

