from djpcms import test
from djpcms.utils.ajax import jredirect



class TestUserViews(test.TestCase):
    appurls  = 'regression.user.appurls'
    
    def _testlogin(self, user, ajax = True):
        url = '/accounts/login/'
        context = self.get(url)
        uni = context['uniform']
        self.assertTrue(uni)
        data = {'username':user.username,
                'password':user.password}
        res = self.post(url, data = data, ajax = ajax, response = True)
             
    def testLoginView(self):
        self._testlogin(self.user)
        