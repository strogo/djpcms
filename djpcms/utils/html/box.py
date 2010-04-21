from base import htmlbase, htmlwrap, htmlcomp

__all__ = ['box']

class box(htmlcomp):
    '''
    A panel is a div component with three subcomponents
        header, body and footer
    '''
    def __init__(self, hd = None, bd = None, ft = None, minimize = False,
                 rounded = True, collapsable = False, collapsed = False, **kwargs):
        super(box,self).__init__('div', **kwargs)
        self.addClass('djpcms-html-box')
        if collapsable:
            self.addClass('collapsable')
            if collapsed:
                self.addClass('collapsed')
        self.paginatePanel(hd, bd, ft)
    
    def paginatePanel(self, hd, bd, ft):
        if hd is not None:
            if isinstance(hd,htmlbase):
                inner = hd
            else:
                inner = htmlwrap('h2', hd)
            self['hd'] = htmlcomp('div', cn = 'hd', inner = inner)
        
        # The body
        if not isinstance(bd,htmlbase):
            bd = htmlwrap('div', bd or u'', cn = 'bd')
        else:
            bd = htmlcomp('div', cn = 'bd', inner = bd)
        
        self['bd'] = bd
        
        # The footer
        #if ft:
        #    self['ft'] = htmlcomp('div', cn = 'ft', inner = ft)
        