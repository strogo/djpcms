from djpcms.utils import mark_safe
from djpcms.template import loader
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
    template_name = 'djpcms/content/box.html'
    collapsable = False
    collapsed = False
    def wrap(self, djp, cblock, html):
        if html:
            c = self._wrap(djp, cblock, html)
            c['classes'] = mark_safe(' '.join(c['classes']))
            return loader.render_to_string(self.template_name, c)
        else:
            return u''
    
    def _wrap(self, djp, cblock, html):
        classes = []
        menulist = []
        if self.collapsable:
            classes.append('collapsable')
            menulist.append(mark_safe('<a class="collapse" href="#">COLLAPSE</a>'))
        if self.collapsed:
            classes.append('collapsed')
        c = {'id': cblock.htmlid(),
             'title': mark_safe(cblock.title),
             'hd': True,
             'bd': html,
             'ft': self.footer(djp,cblock,html),
             'menulist': menulist,
             'classes': classes}
        return c
    
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