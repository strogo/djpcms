from pagination import *
from base import *
from grid960 import *
from autocomplete import *


def box(hd = None, bd = None, ft = None, minimize = False, rounded = True,
        collapsable = False, collapsed = False, classes = None,  id = None,
        delurl = None):
    from djpcms.utils import mark_safe
    from djpcms.template import loader
    classes = classes or []
    menulist = []
    if collapsable:
        classes.append('collapsable')
        menulist.append(mark_safe('<a class="collapse" href="#">COLLAPSE</a>'))
    if collapsed:
        classes.append('collapsed')
    if delurl:
        menulist.append(mark_safe('<a class="deletable ajax" href="%s">DELETE</a>' % delurl))
    c = {'id': id,
         'title': mark_safe(hd),
         'hd': True,
         'bd': mark_safe(bd),
         'ft': mark_safe(ft),
         'menulist': menulist,
         'classes': mark_safe(' '.join(classes))}
    return loader.render_to_string(['box.html',
                                    'content/box.html',
                                    'djpcms/content/box.html'], c)