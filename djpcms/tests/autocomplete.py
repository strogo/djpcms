from django.test import TestCase

from djpcms import forms # RULE 1 import forms from djpcms
from djpcms.views import appsite, appview
from djpcms.tests.conf.test_urls import StrategyApplication
from djpcms.tests.testmodel.models import Strategy
from djpcms.utils import uniforms
from djpcms.tests.testmodel.forms import StrategyForm


class StrategyApplicationWithAutocomplete(StrategyApplication):
    # RULE 2 the search_fields list
    search_fields = ['name','description']
    # RULE 3 the autocomplete view
    autocomplete = appview.AutocompleteView(regex = 'autocompletetest', display = 'name') 


class TestForm(forms.Form):
    strategy = forms.ModelChoiceField(Strategy.objects.all())
    
    
class TestFormMulti(forms.Form):
    strategy = forms.ModelMultipleChoiceField(Strategy.objects.all())
    
    

class TestAutocomplete(TestCase):
    
    def setUp(self):
        appsite.site.unregister(Strategy)
        # RULE 4 register your application
        appsite.site.register('/strategy/',StrategyApplicationWithAutocomplete,model = Strategy)
        
    def testModelChoiceField(self):
        f = TestForm()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategy/autocompletetest/"' in html)
        
    def testModelMultipleChoiceField(self):
        f = TestFormMulti()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategy/autocompletetest/"' in html)
        
    def tearDown(self):
        appsite.site.unregister(Strategy)
        appsite.site.register('/strategy/',StrategyApplication,model = Strategy)
