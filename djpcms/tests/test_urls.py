from djpcms.views.apps import appurls

class ContentArchiveApplication(appurls.ArchiveApplication):
    name       = 'content'
    baseurl    = '/content/'
    date_code  = 'last_modified'


