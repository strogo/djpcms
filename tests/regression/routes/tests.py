from djpcms import test
from djpcms.core.exceptions import AlreadyRegistered

import djpcms


class TestSites(test.TestCase):

    def testMake(self):
        self.assertRaises(AlreadyRegistered,djpcms.MakeSite,__file__)
        site = djpcms.MakeSite(__file__, route = '/extra/')
        self.assertEqual(site.route,'/extra/')
