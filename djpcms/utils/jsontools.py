from time import mktime
from datetime import datetime, date, time
from decimal import Decimal
import json
    
all = ['JSONDateDecimalEncoder', 'date_decimal_hook']

def totimestamp(dte):
    return mktime(dte.timetuple())


def todatetime(tstamp):
    return datetime.fromtimestamp(tstamp)
    

class JSONDateDecimalEncoder(json.JSONEncoder):
    """
    Provide custom serializers for JSON-RPC.
    """
    def default(self, obj):
        if isinstance(obj,datetime):
            return {'__datetime__':totimestamp(obj)}
        elif isinstance(obj, date):
            return {'__date__':totimestamp(obj)}
        elif isinstance(obj, time):
            return {'__time__':totimestamp(obj)}
        elif isinstance(obj, Decimal):
            return {'__decimal__':str(obj)}
        else:
            raise ValueError("%r is not JSON serializable" % (obj,))


def date_decimal_hook(dct):
    if '__datetime__' in dct:
        return todatetime(dct['__datetime__'])
    elif '__date__' in dct:
        return todatetime(dct['__date__']).date()
    elif '__time__' in dct:
        return todatetime(dct['__time__']).time()
    elif '__decimal__' in dct:
        return Decimal(dct['__decimal__'])
    else:
        return dct
    