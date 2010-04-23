from django.utils.safestring import mark_safe

from djpcms.plugins import DJPwrapper
from djpcms.utils.html import box


class simplediv(DJPwrapper):
    name = 'flat-element'
    description = 'div .flat-element'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            return mark_safe(u'\n'.join(['<div id="%s" class="flat-element">' % id,
                                         html,
                                         '</div>']))
        else:
            return u''

class PannelWrapper(DJPwrapper):
    name = 'pannel'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            return mark_safe(u'\n'.join(['<div id="%s" class="flat-pannel">' % id,
                                         html,
                                         '</div>']))
        else:
            return u''

class BoxWrapper(DJPwrapper):
    name = 'box'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            hd = cblock.title
            return box(hd = hd, bd = html, id = id).render()
        else:
            return u''
        
class CollapseWrapper(DJPwrapper):
    name = 'box-collapse'
    description = 'box collapsable'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            hd = cblock.title
            return box(hd = hd, bd = html, id = id, collapsable = True).render()
        else:
            return u''

class CollapsedWrapper(DJPwrapper):
    name = 'box-collapse-closed'
    description = 'box collapsable closed'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            hd = cblock.title
            return box(hd = hd, bd = html, id = id, collapsable = True, collapsed = True).render()
        else:
            return u''
    
    
class BoxWrapper2(DJPwrapper):
    name = 'box compact'
    form_layout = 'onecolumn'
    
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            hd = cblock.title
            return box(hd = hd, bd = html, id = id).render()
        else:
            return u''
        

class centereddiv(DJPwrapper):
    name = 'centered-element'
    description = 'Centered element'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            return mark_safe(u'\n'.join(['<div id="%s" class="%s">' % (id,self.name),
                                         html,
                                         '</div>']))
        else:
            return u''