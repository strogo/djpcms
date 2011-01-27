from djpcms.template import loader

from .pagination import *
from .grid960 import *


def box(hd = None, bd = None, ft = None, minimize = False, rounded = True,
        collapsable = False, collapsed = False, classes = None,  id = None,
        delurl = None):
    classes = classes or []
    menulist = []
    if collapsed:
        classes.append('collapsed')
        collapsable = True
    if collapsable:
        classes.append('collapsable')
        menulist.append('<a class="collapse" href="#">COLLAPSE</a>')
    if delurl:
        menulist.append('<a class="deletable ajax" href="%s">DELETE</a>'.format(delurl))
    c = {'id': id,
         'title': None if not hd else hd,
         'hd': True,
         'bd': None if not bd else bd,
         'ft': None if not ft else ft,
         'menulist': menulist,
         'classes': ' '.join(classes)}
    return loader.render_to_string(['box.html',
                                    'content/box.html',
                                    'djpcms/content/box.html'], c)
    
