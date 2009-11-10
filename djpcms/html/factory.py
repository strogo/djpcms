

class htmlfactory(object):
    
    def __init__(self, htmlclass, **kwargs):
        self.htmlclass = htmlclass
        self.kwargs    = kwargs
        
    def make(self, **attrs):
        attrs.update(self.kwargs)
        return self.htmlclass(**attrs)
        