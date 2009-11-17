

class CustomView(object):
    name         = None
    verbose_name = None
    description  = None
    
    def render(self, request, cl, **kwargs):
        '''
        This function needs to be implemented
        '''
        raise NotImplementedError