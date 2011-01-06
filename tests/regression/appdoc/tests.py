import datetime
import os

from djpcms.test import TestCase
from djpcms.utils.pathtool import parentdir
from djpcms.apps.included.docs import DocApplication


class DocTestApplication(DocApplication):
    inherit    = True
    deflang    = None
    defversion = None
    name = 'test_documentation'
    DOCS_PICKLE_ROOT = parentdir(os.path.abspath(__file__))
    
    def get_path_args(self, lang, version):
        return ('docs',)

appurls = DocTestApplication('/docs/'),



class DocsViewTest(TestCase):
    appurls  = 'regression.appdoc.tests'
    
    def testIndex(self):
        pass
        #context = self.get('/docs/')
        