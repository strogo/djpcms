from datetime import datetime

from django.conf import settings

from pytz import timezone

_citynumber = {'America/Chicago': 64,
               'Europe/London': 136,
               'Europe/Rome': 215}


def tzname(tz = None, dt = None):
    z = timezone(tz or settings.TIME_ZONE)
    l = z.localize(dt or datetime.now())
    return l.tzinfo._tzname


def link(tz = None):
    try:
        z = timezone(tz or settings.TIME_ZONE)
        n = _citynumber.get(str(z),None)
        if n:
            return 'http://www.timeanddate.com/worldclock/city.html?n=%s' % n
        else:
            return None
    except:
        return None
    