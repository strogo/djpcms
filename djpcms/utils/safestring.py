"""
Functions for working with "safe strings": strings that can be displayed safely
without further escaping in HTML. Marking something as a "safe string" means
that the producer of the string has already turned characters that should not
be interpreted by the HTML engine (e.g. '<') into the appropriate entities.
"""
from functools import partial

from .functional import Promise, allow_lazy
from .strings import stringtype, force_str

__all__ = ['mark_safe',
           'escape',
           'conditional_escape']


class SafeData(object):
    pass


class SafeBytes(bytes, SafeData):
    """
    A string subclass that has been specifically marked as "safe" (requires no
    further escaping) for HTML output purposes.
    """
    def __add__(self, rhs):
        """
        Concatenating a safe string with another safe string or safe unicode
        object is safe. Otherwise, the result is no longer safe.
        """
        t = super(SafeString, self).__add__(rhs)
        if isinstance(rhs, SafeStr):
            return SafeStr(t)
        elif isinstance(rhs, SafeBytes):
            return SafeBytes(t)
        return t
        
    def decode(self, *args, **kwargs):
        data = super(SafeBytes,self).decode(*args, **kwargs)
        if isinstance(data, bytes):
            return SafeBytes(data)
        else:
            return SafeStr(data)


class SafeStr(stringtype, SafeData):
    """
    A unicode subclass that has been specifically marked as "safe" for HTML
    output purposes.
    """
    def __add__(self, rhs):
        """
        Concatenating a safe string object with another safe string or safe
        byrtes object is safe. Otherwise, the result is no longer safe.
        """
        t = super(SafeStr, self).__add__(rhs)
        if isinstance(rhs, SafeData):
            return SafeStr(t)
        return t
    
    def encode(self, *args, **kwargs):
        """
        Wrap a call to a normal unicode method up so that we return safe
        results. The method that is being wrapped is passed in the 'method'
        argument.
        """
        data = super(SafeStr,self).encode(*args, **kwargs)
        if isinstance(data, bytes):
            return SafeBytes(data)
        else:
            return SafeStr(data)


def mark_safe(s):
    """
    Explicitly mark a string as safe for (HTML) output purposes. The returned
    object can be used everywhere a string or unicode object is appropriate.

    Can be called multiple times on a single string.
    """
    if isinstance(s, SafeData):
        return s
    if isinstance(s, bytes) or (isinstance(s, Promise) and s._delegate_str):
        return SafeBytes(s)
    if isinstance(s, (stringtype, Promise)):
        return SafeStr(s)
    return SafeStr(force_str(s))


def escape(html):
    """
    Returns the given HTML with ampersands, quotes and angle brackets encoded.
    """
    return mark_safe(force_str(html).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;'))
escape = allow_lazy(escape, stringtype)


def conditional_escape(html):
    """
    Similar to escape(), except that it doesn't operate on pre-escaped strings.
    """
    if isinstance(html, SafeData):
        return html
    else:
        return escape(html)
