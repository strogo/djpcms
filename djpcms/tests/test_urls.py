from djpcms.views import appsite
from djpcms.models import SiteContent

class ContentArchiveApplication(appsite.ArchiveApplication):
    inherit    = True
    name       = 'content'
    baseurl    = '/content/'
    date_code  = 'last_modified'
appsite.site.register(SiteContent,ContentArchiveApplication)

