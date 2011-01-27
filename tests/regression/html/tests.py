from djpcms import test, forms


class TestInputs(test.TestCase):
    
    def create(self, InputClass, **kwargs):
        ts = InputClass(**kwargs)
        html = ts.render()
        self.assertTrue(html.startswith('<input '))
        self.assertTrue(html.endswith('/>'))
        return html
    
    def testTextInput(self):
        html = self.create(forms.TextInput, value='test', name='pippo')
        self.assertTrue('value="test"' in html)
        self.assertTrue('name="pippo"' in html)
        
    def testFailTextInput(self):
        self.assertRaises(TypeError,forms.TextInput, fake='test')