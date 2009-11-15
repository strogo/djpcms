from djpcms.plugins.application import appsite
from djpcms.views.apps import appurls
from djpcms.models import SiteContent

class ContentArchiveApplication(appurls.ArchiveApplication):
    inherit    = True
    name       = 'content'
    baseurl    = '/content/'
    date_code  = 'last_modified'
appsite.site.register(SiteContent,ContentArchiveApplication)

