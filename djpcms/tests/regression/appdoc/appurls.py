import os

from djpcms.views import appsite
from djpcms.utils.pathtool import parentdir
from djpcms.views.apps.docs import DocApplication


class DocTestApplication(DocApplication):
    inherit    = True
    deflang    = None
    defversion = None
    name       = 'test_documentation'
    DOCS_PICKLE_ROOT = parentdir(os.path.abspath(__file__))
    
    def get_path_args(self, lang, version):
        return ('docs',)


appsite.site.register('/docs/', DocTestApplication)


