from base import TemplatePlugin, htmlPlugin, link, spanlink

__all__ = ['linklist','breadcrumbs']


def _add_list_item(name = '', url = None, cn = None, withspan = True, **attrs):
    if withspan:
        a = spanlink(url = url, inner = name, cn = cn)
    else:
        a = link(url = url, inner = name, cn = cn)
    return htmlPlugin(tag = 'li', inner = a.attr(**attrs))


class linklist(htmlPlugin):
    tag = 'ul'
    withspan = False
    
    def addlistitem(self, name, url = None, cn = None, **attrs):
        l = _add_list_item(name, url, cn, self.withspan, **attrs)
        self.append(l)
        return l
    
    
class breadcrumbs(linklist):
    
    def __init__(self, **kwargs):
        self.addclass('breadcrumbs')
    
    def prerender(self):
        # Not enough children, return
        cn = 'breadcrumbs-separator'
        if len(self.children) < 2:
            return
        nc = []
        children = self.children[1:]
        nc.append(self.children[0])
        for c in children:
            nc.append(_add_list_item(cn=cn, withspan = True))
            nc.append(c)
        # last c
        #li = self.last()
        #li.children[0].removeAttr('href')
        self.children = nc
        
        
            
        
        
        