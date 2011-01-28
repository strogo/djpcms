from djpcms import test, forms
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
        
    def testSimpleHtml(self):
        hf = forms.HtmlForm(SimpleForm)
        self.assertTrue(hf.form_class,SimpleForm)
        w = hf.widget(hf.form_class(), action = '/test/')
        self.assertTrue(isinstance(w.form,SimpleForm))
        self.assertEqual(w.attrs['action'],'/test/')
        self.assertEqual(w.attrs['method'],'post')
        
        
        