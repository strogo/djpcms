from djpcms.plugins import DJPwrapper
from djpcms.utils.html import box


class simplediv(DJPwrapper):
    name = 'flat-element'
    description = 'flat element'
    def wrap(self, djp, cblock, html):
        return '' if not html else '<div class="{0}">\n'.format(self.name) + html + '\n</div>'


class PannelWrapper(simplediv):
    name = 'flat-panel'
    description = 'panel'
        

class FlatBox(simplediv):
    name = 'flat-box'
    
    def wrap(self, djp, cblock, html):
        if html:
            title = cblock.title
            bd = '<div class="bd">\n' + html + '\n</div>'
            if title:
                bd = '<div class="hd">\n<h2>' + title + '</h2>\n</div>\n' + bd
            return super(FlatBox,self).wrap(djp,cblock,bd)
        else:
            return ''
    
    
class BoxWrapper(DJPwrapper):
    name = 'box'
    collapsable = False
    collapsed = False
    
    def wrap(self, djp, cblock, html):
        if html:
            classes,deleteurl = self._wrap(djp, cblock, html)
            return box(id = self.id(cblock),
                       hd = cblock.title,
                       bd = html,
                       ft = self.footer(djp,cblock,html),
                       collapsable = self.collapsable,
                       collapsed = self.collapsed,
                       delurl = deleteurl,
                       classes = classes)
        else:
            return ''
    
    def id(self, cblock):
        return None
    
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

        
