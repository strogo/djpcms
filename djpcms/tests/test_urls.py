from djpcms.views import appsite
from djpcms.models import SiteContent

class ContentArchiveApplication(appsite.ArchiveApplication):
    '''
    Simple ArchiveApplication based on the SiteContent model in djpcms
    '''
    inherit    = True
    name       = 'content'
    date_code  = 'last_modified'
    
    
appsite.site.register('/content/', ContentArchiveApplication, model = SiteContent)

