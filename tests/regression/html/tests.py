from djpcms import test, forms


class TestInputs(test.TestCase):
    
    def create(self, InputClass, ty, **kwargs):
        ts = InputClass(value='test', name='pippo', **kwargs)
        html = ts.render()
        self.assertTrue(html.startswith('<input '))
        self.assertTrue(html.endswith('/>'))
        self.assertTrue('type="{0}"'.format(ty) in html)
        self.assertTrue('value="test"' in html)
        self.assertTrue('name="pippo"' in html)
        return ts
    
    def testTextInput(self):
        self.create(forms.TextInput, 'text')
        
    def testSubmitInput(self):
        self.create(forms.SubmitInput, 'submit')
        
    def testPasswordInput(self):
        self.create(forms.PasswordInput, 'password')
        
    def testClasses(self):
        ts = self.create(forms.TextInput, 'text', cn = 'ciao')
        self.assertTrue(ts.hasClass('ciao'))
        ts = self.create(forms.TextInput, 'text', cn = 'ciao ciao')
        self.assertTrue(ts.hasClass('ciao'))
        html = ts.render()
        self.assertTrue('class="ciao"' in html)
        ts.removeClass('ciao')
        self.assertFalse(ts.hasClass('ciao'))
        #lets try a jQuery type thing
        ts.addClass('pippo bravo').addClass('another').removeClass('bravo')
        self.assertTrue(ts.hasClass('pippo'))
        self.assertTrue(ts.hasClass('another'))
        self.assertFalse(ts.hasClass('bravo'))
        html = ts.render()
        self.assertTrue('class="pippo another"' in html or
                        'class="another pippo"' in html)
        
    def testFailTextInput(self):
        self.assertRaises(TypeError,forms.TextInput, fake='test')
        
    def testList(self):
        li = forms.List()
        self.assertEqual(len(li),0)
        li = forms.List(['a list item','another one'])
        self.assertEqual(len(li),2)
        html = li.render()
        self.assertTrue('<ul>' in html)
        self.assertTrue('</ul>' in html)
        self.assertTrue('<li>a list item</li>' in html)
        self.assertTrue('<li>another one</li>' in html)
