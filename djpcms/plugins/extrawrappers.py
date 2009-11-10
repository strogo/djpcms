from djpcms.plugins.wrapper import ContentWrapperHandler, add_content_wrapper
from djpcms.html import box


class BoxWrapper(ContentWrapperHandler):
    
    def wrap(self, cblock, request, view):
        html = self.inner(cblock, request, view)
        hd = cblock.plugin.title
        return box(hd = hd, bd = html).render()

add_content_wrapper('simple box',BoxWrapper())


    
class BoxWrapper2(ContentWrapperHandler):
    form_layout = 'onecolumn'
    
    def wrap(self, cblock, request, view):
        html = self.inner(cblock, request, view)
        hd = cblock.plugin.title
        return box(hd = hd, bd = html).render()
    
add_content_wrapper('compact box',BoxWrapper2())