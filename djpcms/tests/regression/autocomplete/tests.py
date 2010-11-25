from djpcms.test import TestCase

from regression.autocomplete.models import Strategy, TestForm, TestFormMulti
    
    

class TestAutocomplete(TestCase):
    appurls = 'regression.autocomplete.appurls'
        
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