from django.template import loader, RequestContext

from djpcms import register_view_method
from djpcms.utils import version

def poweredby(cl, *args):
    '''
    Information about the packages used to power the web-site
    '''
    v = version.get()
    p = v.pop('python')
    d = v.pop('django')
    c = {'python': p.get('version'),
         'django': d.get('version'),
         'other':  v.values()}
    return loader.render_to_string(['/bits/powered_by.html',
                                    'djpcms/bits/powered_by.html'],
                                    c)
register_view_method(poweredby)