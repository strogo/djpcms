from djpcms.forms.html import BaseMedia


class FormLayout(BaseMedia):
    '''Base form class for programmatic form layout design'''
    
    def render(self):
        raise NotImplementedErrror