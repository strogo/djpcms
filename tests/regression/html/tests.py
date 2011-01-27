from djpcms import test
from djpcms import forms


class TestInputs(test.TestCase):
    
    def buildInput(self, InputClass, **attrs):
        ti = InputClass(**attrs)
        html = ti.render()
        self.assertTrue(html.startswith('<input'))
        self.assertTrue(html.endswith('/>'))
        return ti,html
        
    def testTextInput(self):
        ti,html = self.buildInput(forms.TextInput, value='test', name='pippo')
        self.assertTrue('value="test"' in html)
        self.assertTrue('name="pippo"' in html)
    
    def testTextFail(self):
        self.assertRaises(TypeError,
                          forms.TextInput,
                          fakeattr = 'bo')