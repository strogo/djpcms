import os

from djpcms.views import appsite, appview
from djpcms.utils.pathtool import parentdir
from djpcms.apps.included import archive, vanilla, docs
from djpcms.models import SiteContent

from regression.rootappnav.models import Strategy
    

class RandomApplication(appsite.Application):
    '''A simple application without database model'''
    name = 'random application'
    home = appview.View(isapp = True, in_navigation = True)


class ContentArchiveApplication(archive.ArchiveApplication):
    '''
    Simple ArchiveApplication based on the SiteContent model in djpcms
    '''
    inherit    = True
    name       = 'content'
    date_code  = 'last_modified'


class DocTestApplication(docs.DocApplication):
    inherit    = True
    deflang    = None
    defversion = None
    name       = 'test_documentation'
    DOCS_PICKLE_ROOT = parentdir(os.path.abspath(__file__))
    
    def get_path_args(self, lang, version):
        return ('docs',)
    
    
#Register few applications for testing
appurls = (
           archive.ArchiveApplication('/content/',
                                      SiteContent, 
                                      name = 'content',
                                      date_code  = 'last_modified'),
           DocTestApplication('/docs/'),
           RandomApplication('/random/'),
           vanilla.Application('/', Strategy),
           )