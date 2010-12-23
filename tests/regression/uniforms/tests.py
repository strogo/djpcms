from django.test import TestCase

from djpcms import forms
from djpcms.utils import uniforms
from regression.uniforms.forms import StrategyForm


class TestForm(forms.Form):
    is_company = forms.CharField(label="company", required=False, widget=forms.CheckboxInput())
    email = forms.CharField(label="email", max_length=30, required=True, widget=forms.TextInput())
    password1 = forms.CharField(label="password", max_length=30, required=True, widget=forms.PasswordInput())
    password2 = forms.CharField(label="re-enter password", max_length=30, required=True, widget=forms.PasswordInput())
    first_name = forms.CharField(label="first name", max_length=30, required=True, widget=forms.TextInput())
    last_name = forms.CharField(label="last name", max_length=30, required=True, widget=forms.TextInput())

    

    
class TestUniForms(TestCase):
    
    def test_as_uni_form(self):
        uni = uniforms.UniForm(TestForm())
        html = uni.render()
        self.assertTrue("<td>" not in html)
        self.assertTrue("id_is_company" in html)
        
    def test_uni_with_formlets(self):
        f = StrategyForm()
        uni = uniforms.UniForm(f)
        html = uni.render()
        self.assertTrue("<td>" in html)
        self.assertTrue("id_name" in html)
        self.assertTrue("id_description" in html)
        
        