
from django.conf import settings

_tz = {'Europe/London': 136}

def link(tz = None):
    tz = tz or settings.TIME_ZONE
    n  = _tz.get(tz, None)
    if n:
        return 'http://www.timeanddate.com/worldclock/city.html?n=%s' % n
    else:
        return ''
    