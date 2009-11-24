from django.utils.safestring import mark_safe

from djpcms.plugins import DJPwrapper
from djpcms.utils.html import box


class simplediv(DJPwrapper):
    name = 'flat-element'
    description = 'div .flat-element'
    def wrap(self, djp, cblock, html):
        id = cblock.htmlid()
        return mark_safe(u'\n'.join(['<div id="%s" class="flat-element">' % id,
                                     html,
                                     '</div>']))

class BoxWrapper(DJPwrapper):
    name = 'box'
    def wrap(self, djp, cblock, html):
        id = cblock.htmlid()
        hd = cblock.title
        return box(hd = hd, bd = html, id = id).render()
    
    
class BoxWrapper2(DJPwrapper):
    name = 'compact-box'
    form_layout = 'onecolumn'
    
    def wrap(self, djp, cblock, html):
        id = cblock.htmlid()
        hd = cblock.title
        return box(hd = hd, bd = html, id = id).render()