
from jsonbase import HeaderBody


__all__ = ['dialog']


class dialog(HeaderBody):
    '''
    jQuery UI dialog
    '''
    def __init__(self, hd = '', bd = None, **kwargs):
        self.bd         = bd
        self.options    = self.get_options(hd,**kwargs)
        self.buttons    = []
        
    def get_options(self, hd, **kwargs):
        return {'modal': kwargs.get('modal',False),
                'draggable': kwargs.get('draggable',True),
                'resizable': kwargs.get('resizable',True),
                'height':    kwargs.get('height','auto'),
                'width':     kwargs.get('width',300),
                'title':     hd,
                'dialogClass': kwargs.get('dialogClass','')}
        
    def header(self):
        return 'dialog'
    
    def body(self):
        return {'html':self.bd,
                'options':self.options,
                'buttons':self.buttons}
        
    def addbutton(self, name, url = None, func = None, close = True):
        self.buttons.append({'name':name,
                             'url':url,
                             'func':func,
                             'close':close})