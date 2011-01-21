from djpcms.test import TestCase

from .forms import *

class SimpleForm(TestCase):
    
    def testSimpleFactory(self):
        self.assertTrue(len(LoginForm.fields),2)
        form = LoginForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidSimpleBound(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = LoginForm(data = {prefix+'username':'pinco',
                                 prefix+'password':'blabla'},
                         prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['username'],'pinco')
        self.assertEqual(form.data['password'],'blabla')