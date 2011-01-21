from djpcms import test
from djpcms import sites


class TestCMS(test.TestCase):
    backend = 'django'
    
    def setUp(self):
        self.oldbackend = sites.settings.CMS_ORM
        sites.settings.CMS_ORM = self.backend
        super(TestCMS).setUp(self)
        
    def testImport(self):
        pass
        
    def tearDown(self):
        sites.settings.CMS_ORM = self.oldbackend