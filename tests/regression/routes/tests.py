from djpcms import test
from djpcms.core.exceptions import AlreadyRegistered

import djpcms


class TestSites(test.TestCase):

    def testMake(self):
        self.assertRaises(AlreadyRegistered,djpcms.MakeSite,__file__)
        site = djpcms.MakeSite(__file__, route = '/extra/')
        self.assertEqual(site.route,'/extra/')
        
    def testClenUrl(self):
        p = self.makepage(bit = 'test')
        self.assertEqual(p.url,'/test/')
        res = self.get('/test', status = 302, response = True)
        self.assertEqual(res['location'],'http://testserver/test/')
        res = self.get('/test////', status = 302, response = True)
        self.assertEqual(res['location'],'http://testserver/test/')
        
