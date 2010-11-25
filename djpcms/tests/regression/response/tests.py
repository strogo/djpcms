from djpcms.test import TestCase
from djpcms.conf import settings

from regression.response.models import Strategy

class TestDjpResponse(TestCase):
    '''Test functions in DjpResponse instances.'''
    appurls = 'regression.response.appurls'
    
    def testOwnPageSimple(self):
        context = self.get('/')
        self.assertTrue(context['djp'].has_own_page())
        self.makepage('search',Strategy)
        context = self.get('/strategies/')
        self.assertTrue(context['djp'].has_own_page())
        
    def testOwnPageApplication(self):
        self.login()
        link = '<a href="/edit-content/strategies/add/">edit</a>'
        self.makepage('search',Strategy)
        response = self.get('/strategies/add/', response = True)
        self.assertFalse(response.context['djp'].has_own_page())
        self.assertTrue(link not in response.content)
        self.makepage('add',Strategy)
        response = self.get('/strategies/add/', response = True)
        self.assertTrue(response.context['djp'].has_own_page())
        self.assertTrue(link in response.content)