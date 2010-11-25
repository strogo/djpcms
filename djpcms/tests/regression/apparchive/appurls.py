from djpcms.views import appsite
from djpcms.views.apps import archive
from djpcms.models import SiteContent


class ContentArchiveApplication(archive.ArchiveApplication):
    '''Simple ArchiveApplication based on the SiteContent model in djpcms
    '''
    inherit    = True
    name       = 'content'
    date_code  = 'last_modified'

#Register few applications for testing
appsite.site.register('/content/', ContentArchiveApplication, model = SiteContent)


