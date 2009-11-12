from django import forms

__all__ = ['ExtendedModelForm']



class ExtendedModelForm(forms.ModelForm):
    
    def __init__(self, **kwargs):
        super(ExtendedModelForm,self).__init__(**kwargs)