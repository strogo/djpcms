from base import htmlPlugin, div, link, button
from form import form


class box(htmlPlugin):
    tag = 'div'
    '''
    A panel is a div component with three subcomponents
        header, body and footer
    '''
    def __init__(self, hd = None, bd = None, ft = None, minimize = False, rounded = True, hideshow = False, **kwargs):
        self.addclass('djpcms-html-box')
        if hideshow:
            self.addclass('hideshow')
        else:
            if rounded:
                self.addclass('rounded')
        self.paginatePanel(hd, bd, ft)
    
    def paginatePanel(self, hd, bd, ft):
        if hd is not None:
            if isinstance(hd,htmlPlugin):
                inner = hd
            else:
                inner = htmlPlugin(tag = 'h2', inner = hd)
            self['hd'] = div(cn = 'hd', inner = inner)
        
        # The body
        self['bd'] = div(cn = 'bd', inner = bd)
        
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