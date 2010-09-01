import os

from djpcms.views import appsite
from djpcms.utils.pathtool import parentdir
from djpcms.views.apps import archive
from djpcms.models import SiteContent
from djpcms.views.apps.docs import DocApplication


class ContentArchiveApplication(archive.ArchiveApplication):
    '''
    Simple ArchiveApplication based on the SiteContent model in djpcms
    '''
    inherit    = True
    name       = 'content'
    date_code  = 'last_modified'


class DocTestApplication(DocApplication):
    inherit    = True
    deflang    = None
    defversion = None
    name       = 'test_documentation'
    DOCS_PICKLE_ROOT = parentdir(os.path.abspath(__file__))
    
    def get_path_args(self, lang, version):
        return ('docs',)
    
    
appsite.site.register('/content/', ContentArchiveApplication, model = SiteContent)
appsite.site.register('/docs/', DocTestApplication)

