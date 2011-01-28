from djpcms import test, sites
from djpcms.apps.included.user import LoginForm
        
        
class TestUserMixin(object):
    
    def _testlogin(self, user, ajax = True):
        url = '/accounts/login/'
        context = self.get(url)
        uni = context['uniform']
        self.assertTrue(uni)
        data = {'username':user.username,
                'password':user.password}
        res = self.post(url, data = data, ajax = ajax, response = True)
             
    def __testLoginView(self):
        self._testlogin(self.user)
        
    def testLoginForm(self):
        self.assertTrue(len(LoginForm.base_fields),2)
        form = LoginForm()
        self.assertFalse(form.is_bound)
        self.assertFalse(form.is_valid())
        
    def testValidLoginForm(self):
        prefix = 'sjkdcbksdjcbdf-'
        form = LoginForm(data = {prefix+'username':'pinco',
                                 prefix+'password':'blabla'},
                         prefix = prefix)
        self.assertTrue(form.is_bound)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.data['username'],'pinco')
        self.assertEqual(form.data['password'],'blabla')
        

@test.skipIf('django' not in sites.modelwrappers,
             'django is not installed')
class TestDjangoUser(test.TestCase,TestUserMixin):
    appurls = 'regression.user.appurls_django'
    
    
@test.skipIf('stdnet' not in sites.modelwrappers,
             'python-stdnet is not installed')
class TestStdnetUser(test.TestCase,TestUserMixin):
    appurls = 'regression.user.appurls_stdnet'
    
    def installed_apps(self):
        return ['stdnet.contrib.sessions']
    