from django import template
from django.utils.safestring import mark_safe

from djpcms.html import htmlPlugin

register = template.Library()    
    
def _grid_widget(inner, kclass = None, wrap = True):
    kclass = kclass or 'white-panel'
    return template.loader.render_to_string('djpcms/layouts/bits/grid-element.html',
                                            {'html': inner,
                                             'kclass': kclass,
                                             'wrap': wrap})

def grid_widget(inner, kclass = None):
    return _grid_widget(inner, kclass)
grid_widget = register.filter(grid_widget)

def grid_wrap(inner):
    if isinstance(inner,htmlPlugin):
        return inner.render_as_widget()
    else:
        return _grid_widget(inner, wrap =  False)
grid_wrap = register.filter(grid_wrap)


def title_widget(inner, url = None):
    kclass = 'title-panel'
    if url:
        inner = '<a href="%s">%s</a>' % (url,inner)
    inner = ['<span></span>',
             '<div>',
             '%s' % inner,
             '</div>']
    return _grid_widget(mark_safe(u'\n'.join(inner)), kclass)
title_widget = register.filter(title_widget)