from djpcms.template import loader, mark_safe
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
    name = 'panel'
    def wrap(self, djp, cblock, html):
        if html:
            id = cblock.htmlid()
            return mark_safe(u'\n'.join(['<div id="%s" class="flat-panel">' % id,
                                         html,
                                         '</div>']))
        else:
            return u''

class BoxWrapper(DJPwrapper):
    name = 'box'
    collapsable = False
    collapsed = False
    def wrap(self, djp, cblock, html):
        if html:
            classes,deleteurl = self._wrap(djp, cblock, html)
            return box(id = cblock.htmlid(),
                       hd = cblock.title,
                       bd = html,
                       ft = self.footer(djp,cblock,html),
                       collapsable = self.collapsable,
                       collapsed = self.collapsed,
                       delurl = deleteurl,
                       classes = classes)
        else:
            return u''
    
    def _wrap(self, djp, cblock, html):
        return None,None
    
    def footer(self, djp, cblock, html):
        return ''
        
class CollapseWrapper(BoxWrapper):
    name = 'box-collapse'
    description = 'box collapsable'
    collapsable = True

class CollapsedWrapper(BoxWrapper):
    name = 'box-collapse-closed'
    description = 'box collapsable closed'
    collapsable = True
    collapsed = True
        

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