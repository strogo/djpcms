from base import htmlbase, htmlsmall, htmlcomp

__all__ = ['box']

class box(htmlcomp):
    '''
    A panel is a div component with three subcomponents
        header, body and footer
    '''
    def __init__(self, hd = None, bd = None, ft = None, minimize = False,
                 rounded = True, hideshow = False, **kwargs):
        super(box,self).__init__('div', **kwargs)
        self.addClass('djpcms-html-box')
        if hideshow:
            self.addClass('hideshow')
        else:
            if rounded:
                self.addClass('rounded')
        self.paginatePanel(hd, bd, ft)
    
    def paginatePanel(self, hd, bd, ft):
        if hd is not None:
            if isinstance(hd,htmlbase):
                inner = hd
            else:
                inner = htmlsmall('h2', hd)
            self['hd'] = htmlcomp('div', cn = 'hd', inner = inner)
        
        # The body
        self['bd'] = htmlcomp('div', cn = 'bd', inner = bd)
        
        # The footer
        if ft:
            self['ft'] = htmlcomp('div', cn = 'ft', inner = ft)
        