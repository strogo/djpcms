from djpcms.apps.included.archive import ArchiveApplication
from djpcms.models import SiteContent

appurls = ArchiveApplication('/content/',
                             SiteContent,
                             name    = 'content',
                             date_code  = 'last_modified'),


