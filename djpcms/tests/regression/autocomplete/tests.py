from djpcms.test import TestCase
from djpcms.views import appsite, appview

from regression.autocomplete.models import Strategy

# RULE 1 import forms from djpcms
from djpcms import forms

class TestForm(forms.Form):
    strategy = forms.ModelChoiceField(Strategy.objects.all())
    
    
class TestFormMulti(forms.Form):
    strategy = forms.ModelMultipleChoiceField(Strategy.objects.all())


class ApplicationWithAutocomplete(appsite.ModelApplication):
    # RULE 2 the search_fields list
    search_fields = ['name','description']
    # RULE 3 the autocomplete view
    autocomplete = appview.AutocompleteView(regex = 'autocompletetest',
                                            display = 'name')     

# RULE 4 register as usual
appurls = ApplicationWithAutocomplete('/strategies/', Strategy),
    

class TestAutocomplete(TestCase):
    '''Autocomplete functionalities. Autocomplete widgets are implemented
in :mod:`djpcms.utils.html.autocomplete`.'''

    appurls = 'regression.autocomplete.tests'
        
    def testModelChoiceField(self):
        f = TestForm()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategies/autocompletetest/"' in html)
        
    def testModelMultipleChoiceField(self):
        f = TestFormMulti()
        html = f.as_table()
        self.assertFalse('<select' in html)
        self.assertTrue('href="/strategies/autocompletetest/"' in html)