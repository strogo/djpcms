
from django.template import loader, Context

class htmlbase(object):
    
    def get_template(self):
        raise NotImplementedError
    
    def get_content(self):
        raise NotImplementedError
    
    def render(self):
        return loader.render_to_string(self.get_template(),
                                       self.get_content())