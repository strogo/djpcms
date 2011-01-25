import sys
from datetime import datetime, date, time
from decimal import Decimal

__all__ = ['encode_str','force_str','stringtype']


# Python 2.6 to Python 3 hack
try:
    stringtype = unicode
except NameError:
    stringtype = str


protected_types = (int, datetime, date, time, float, Decimal)


class StrAndUnicode(object):
    """
    A class whose __str__ returns its __unicode__ as a UTF-8 bytestring.

    Useful as a mix-in.
    """
    def __str__(self):
        return self.__unicode__().encode('utf-8')


def encode_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a bytestring version of 's',
encoded as specified in 'encoding'.
If strings_only is True, don't convert (some)
non-string-like objects."""
    if isinstance(s,bytes):
        if encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s
        
    if strings_only and (s is None or isinstance(s, protected_types)):
        return s
        
    if not isinstance(s, stringtype):
        s = stringtype(s)
    
    return s.encode(encoding, errors)
    
    
def force_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to encode_str, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, stringtype):
        return s
    if strings_only and (s is None or isinstance(s, protected_types)):
        return s
    if isinstance(s,bytes):
        return s.decode(encoding,errors)
    return stringtype(s)


