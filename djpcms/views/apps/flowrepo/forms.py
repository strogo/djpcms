from django import forms

from flowrepo.models import CategoryType


class ChangeCategory(forms.Form):
    category_name = forms.ModelChoiceField(queryset = CategoryType.objects.all(),
                                           empty_label=None)
    




