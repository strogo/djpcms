from djpcms import test

import djpcms


class TestSites(test.TestCase):

    def testMake(self):
        site = djpcms.MakeSite(__file__)
        self.assertEqual(site.route,'/')
