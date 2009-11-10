from djpcms.settings import HTML_CLASSES

from base import htmlPlugin, div, link, button
from form import form


class panel(htmlPlugin):
    tag = 'div'
    '''
    A panel is a div component with three subcomponents
        header, body and footer
    '''
    def __init__(self, hd = None, bd = None, ft = None, minimize = False, **kwargs):
        self.addclass(HTML_CLASSES.module_class)
        self.paginatePanel(hd, bd, ft)
    
    def paginatePanel(self, hd, bd, ft):
        if hd:
            self['hd'] = div(cn = 'hd', inner = htmlPlugin(tag = 'div', inner = hd))
        
        # The body
        self.bd = div(cn = 'g-wrap')
        self.append(div(cn = 'bd').append(div(cn = 'bd-elem').append(self.bd)))
        self.bd.append(bd)
        
        # The footer
        if ft:
            self['ft'] = div(cn = 'ft', inner = ft)
        
    def wrap_internal_widget(self, el):
        return el
            
    def addeditlink(self, bodyelem):
        if bodyelem:
            bodyelem.append(link(url = '#', inner='Cancel', cn = 'editbox-cancel'))
        l = link(url = '#', cn = 'editbox').attr(title = 'edit')
        self.hd.append(l)
        elem = self.appendtobody(bodyelem).addclass('editbox-target')
            
    def appendtobody(self, bd):
        return self.bd.append(bd)
            

class editpanel(panel):
    tag = 'form'
    editbox_target_class = 'editbox-target'
    '''
    An editable panel
    '''
    def __init__(self, **kwargs):
        super(editpanel,self).__init__(**kwargs)
        self.addclass('editable')
        try:
            ft = self.ft
        except:
            ft = div(cn = 'ft')
            self['ft'] = ft
        ft.css(display = 'none')
        ft = ft.addclass('buttonpane')
        ft.append(button(inner='Cancel').attr(name = 'cancel'))
        ft.append(button(inner="OK").attr(name = 'edit_labels'))
        link(url = '#', cn = 'editbox').attr(title = 'edit').appendTo(self.hd)
        
    
    