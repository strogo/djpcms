from djpcms import test
from djpcms.core.exceptions import *
from djpcms.apps.site import ApplicationSites


class TestSites(test.TestCase):
    
    def makesite(self):
        self.sites.clear()
        self.sites = ApplicationSites()
        
    def testLoadError(self):
        '''No sites created. Load should raise an error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)