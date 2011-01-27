from random import randint
from djpcms import forms


class SimpleForm(forms.Form):
    name = forms.CharField(max_length = 64)
    age = forms.IntegerField(default = lambda b : randint(10,100))