from djpcms import sites, test, MakeSite
from djpcms.apps.site import ApplicationSites
from djpcms.core.exceptions import ImproperlyConfigured


class TestSites(test.TestCase):
    
    def makesite(self):
        self.sites.clear()
        self.sites = ApplicationSites()
        
    def testLoadError(self):
        '''No sites created. Load should raise an ImproperlyConfigured
        error'''
        self.assertRaises(ImproperlyConfigured,self.sites.load)
        
    @test.skipIf('stdnet' not in sites.modelwrappers,
                 'python-stdnet is not installed')
    def testStdnetApp(self):
        site = MakeSite(__file__,
                        APPLICATION_URLS = 'regression.sites.stdnet_urls')
        self.assertEqual(len(sites),1)
        self.assertEqual(sites[0],site)
        self.assertFalse(sites.isloaded)
        
    def testUser(self):
        sites = self.sites
        self.assertEqual(sites.User,None)