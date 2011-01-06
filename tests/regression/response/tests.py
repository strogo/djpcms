from djpcms.test import TestCase
from djpcms.apps.included import vanilla

from regression.response.models import Strategy


appurls = vanilla.Application('/strategies/',Strategy),


class TestDjpResponse(TestCase):
    '''Test functions in DjpResponse instances.'''
    appurls = 'regression.response.tests'
    
    def testOwnPageSimple(self):
        context = self.get('/')
        self.assertTrue(context['djp'].has_own_page())
        self.makepage('search',Strategy)
        context = self.get('/strategies/')
        self.assertTrue(context['djp'].has_own_page())
        
    def testOwnPageApplication(self):
        self.login()
        self.makepage('search',Strategy)
        response = self.get('/strategies/add/', response = True)
        self.assertFalse(response.context['djp'].has_own_page())
        self.makepage('add',Strategy)
        response = self.get('/strategies/add/', response = True)
        self.assertTrue(response.context['djp'].has_own_page())