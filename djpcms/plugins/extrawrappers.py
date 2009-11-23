from django.utils.safestring import mark_safe

from djpcms.plugins import DJPwrapper
from djpcms.html import box


class simplediv(DJPwrapper):
    name = 'flat-element'
    description = 'div .flat-element'
    def wrap(self, djp, cblock, html):
        return mark_safe(u'\n'.join(['<div class="flat-element">',
                                     html,
                                     '</div>']))

class BoxWrapper(DJPwrapper):
    name = 'box'
    def wrap(self, djp, cblock, html):
        hd = cblock.title
        return box(hd = hd, bd = html).render()
    
    
class BoxWrapper2(DJPwrapper):
    name = 'compact-box'
    form_layout = 'onecolumn'
    
    def wrap(self, djp, cblock, html):
        hd = cblock.title
        return box(hd = hd, bd = html).render()