from djpcms import sites
from djpcms.apps.included import archive
from djpcms.apps.included.static import Static
from .models import Issue


class IssueTraker(archive.ArchiveApplication):
    inherit = True
    date_code = 'timestamp'
    STATUS_CODES = (
                    (1, 'Open'),
                    (2, 'Working'),
                    (3, 'Closed'),
                    )
    PRIORITY_CODES = (
                      (1, 'Bloker'),
                      (2, 'Critical'),
                      (3, 'High'),
                      (4, 'Medimu'),
                      (5, 'Low'),
                      )
    
    
appurls = (
           Static(sites.settings.MEDIA_URL, show_indexes=True),
           IssueTraker('/',Issue),
           )
    

    