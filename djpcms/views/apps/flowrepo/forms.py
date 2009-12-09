from django import forms

from flowrepo.models import CategoryType, Image


class ChangeCategory(forms.Form):
    category_name = forms.ModelChoiceField(queryset = CategoryType.objects.all(),
                                           empty_label=None)
    
class ChangeImage(forms.Form):
    image   = forms.ModelChoiceField(queryset = Image.objects.all(), empty_label=None)
    class_name = forms.CharField(max_length = 100, required = False)



