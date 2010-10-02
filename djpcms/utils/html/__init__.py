from pagination import *
from base import *
from grid960 import *
from autocomplete import *


def box(hd = None, bd = None, ft = None, minimize = False, rounded = True,
        collapsable = False, collapsed = False, classes = None,  id = None):
    from djpcms.utils import mark_safe
    from djpcms.template import loader
    classes = classes or []
    menulist = []
    if collapsable:
        classes.append('collapsable')
        menulist.append(mark_safe('<a class="collapse" href="#">COLLAPSE</a>'))
    if collapsed:
        classes.append('collapsed')
    c = {'id': id,
         'title': hd,
         'hd': True,
         'bd': bd,
         'ft': ft,
         'menulist': menulist,
         'classes': mark_safe(' '.join(classes))}
    return loader.render_to_string(['box.html',
                                    'content/box.html',
                                    'djpcms/content/box.html'], c)