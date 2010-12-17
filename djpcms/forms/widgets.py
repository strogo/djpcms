from django import forms
from django.forms.widgets import media_property

__all__ = ['Select',
           'Textarea',
           'TextInput',
           'CheckboxInput',
           'HiddenInput',
           'PasswordInput',
           'media_property']


Select    = forms.Select
Textarea  = forms.Textarea
TextInput = forms.TextInput
CheckboxInput = forms.CheckboxInput
HiddenInput = forms.HiddenInput
PasswordInput = forms.PasswordInput