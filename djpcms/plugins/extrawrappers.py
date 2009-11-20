from djpcms.plugins.wrapper import ContentWrapper, add_content_wrapper
from djpcms.html import box


class BoxWrapper(ContentWrapper):
    
    def wrap(self, djp, cblock, html):
        hd = cblock.title
        return box(hd = hd, bd = html).render()
add_content_wrapper(BoxWrapper,'boxwrapper','Box with title')


    
class BoxWrapper2(ContentWrapper):
    form_layout = 'onecolumn'
    
    def wrap(self, djp, cblock, html):
        hd = cblock.title
        return box(hd = hd, bd = html).render()
add_content_wrapper(BoxWrapper2,'compactbox','Compact Box with title')