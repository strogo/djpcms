from djpcms.test import TestCase
from djpcms.apps.included.user import LoginForm
from djpcms.forms.cms import PageForm


class SimpleForm(TestCase):
    
    def testSimpleFactory(self):
        self.assertTrue(len(LoginForm.base_fields),2)
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
        
    def testvalidPageForm(self):
        