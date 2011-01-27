from djpcms import test
from .forms import SimpleForm


class TestSimpleForm(test.TestCase):
    
    def testSimpleFactory(self):
        self.assertTrue(len(SimpleForm.base_fields),2)
        form = SimpleForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidSimpleBound(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = SimpleForm(data = {prefix+'name':'pinco'},
                         prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.data['name'],'pinco')
        self.assertTrue(form.data['age'])
        