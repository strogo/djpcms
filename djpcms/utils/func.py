import re

from django import forms
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe


def slugify(value, rtx = '-'):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return mark_safe(re.sub('[-\s]+', rtx, value))

def isforminstance(f):
    '''
    whether f is an instance of a django Form or ModelForm
    '''
    return isinstance(f,forms.Form) or isinstance(f,forms.ModelForm)

def data2url(url,data):
    ps = []
    for k,v in data.items():
        v = v or ''
        ps.append('%s=%s' % (k,v))
    p = '&'.join(ps)
    return u'%s?%s' % (url,p)

class PathList(list):
    def __unicode__(self):
        return u' > '.join([smart_unicode(page) for page in self])
    
    
def force_number_insert(n, d, v):
    if d.has_key(n):
        force_number_insert(n+0.1, d, v)
    else:
        d[n] = v