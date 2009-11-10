from base import htmlPlugin, link

__all__ = ['feeds']

class feeds(htmlPlugin):
    tag = 'div'
    
    def __init__(self, numResults = 10, **kwargs):
        self.addclass(self.ajax.FEEDS_HTML_CLASS).addclass(self.ajax.GRID_WIDGET_CLASS)
        self.append(htmlPlugin(tag = 'numResults', inner = numResults).css(display = 'none'))
        
    def appendfeed(self, url, name = ''):
        a = link(url = url, inner = name)
        self.append(a) 
        
        