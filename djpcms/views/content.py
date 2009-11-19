
from djpcms.utils.navigation import Navigator, Breadcrumbs

def basecontent(djp):
    return {'sitenav':          Navigator(djp),
            'breadcrumbs':      Breadcrumbs(djp)}
    