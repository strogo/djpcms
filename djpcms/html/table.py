from base import htmlPlugin

__all__ = ['table']

class table(htmlPlugin):
    tag = 'table'
    
    def __init__(self, cols = 2, *args, **kwargs):
        self['tbody'] = htmlPlugin(tag = 'tbody')
        self.cols = cols
        
    def addheader(self, *args):
        key = 'thead'
        if not hasattr(self,key):
            html = htmlPlugin(tag = key)
            self.children.insert(0,html)
            row  = htmlPlugin(tag = 'tr').appendTo(html)
            object.__setattr__(self,key,html)
            for a in args:
                row.append(htmlPlugin(tag = 'th', inner = a))
            return html
        else:
            return self.children[0]
        
    def addrow(self, *args, **kwargs):
        colspan = kwargs.pop('colspan',None)
        N       = min(self.cols,len(args))
        row     = htmlPlugin(tag = 'tr')
        for i in range(0,N):
            td = htmlPlugin(tag = 'td', inner = args[i])
            if colspan:
                td.attrs['colspan'] = colspan
            row.append(td)
        self.tbody.append(row)