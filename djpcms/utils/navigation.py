'''
Utility module for creating a navigation list
'''

from djpcms.settings import HTML_CLASSES
from djpcms.utils import lazyattr    


class lazycounter(object):
    '''
    A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, djp, *args, **kwargs):
        obj = super(lazycounter, cls).__new__(cls)
        obj.djp     = djp
        obj.kwargs  = kwargs
        return obj

    def __len__(self):
        return len(self.elems())
    
    def count(self):
        return len(self)
    
    def __iter__(self):
        return self.items()

    @lazyattr
    def elems(self):
        return self._items(**self.kwargs)
    
    def items(self):
        elems = self.elems()
        for elem in elems:
            yield elem
            
    def _items(self, **kwargs):
        '''
        The only function to implement.
        It should return an iterable object (but not a generator)
        '''
        raise NotImplementedError
    


class Navigator(lazycounter):
    '''
    A navigator for a web site
    '''
    def make_item(self, djp, classes):
        return {'name':    djp.linkname,
                'url':     djp.url,
                'classes': u' '.join(classes),
                'nav':     Navigator(djp, **self.kwargs)}
    
    def buildselects(self, djp, urlselects):
        parent = djp.parent
        if parent:
            urlselects.append(djp.url)
            return self.buildselects(parent, urlselects)
        else:
            return djp
        
    def _items(self, urlselects = None, secondary_after = 100, **kwargs):
        djp        = self.djp
        if urlselects is None:
            urlselects = []
            djp = self.buildselects(djp,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn        = HTML_CLASSES.secondary_in_list
        request    = djp.request
        children   = djp.children
        items      = []
        for djp in children:
            nav = djp.in_navigation()
            if not nav:
                continue
            url     = djp.url
            classes = []
            if djp.in_navigation() > secondary_after:
                classes.append(scn)
            if url in urlselects:
                classes.append(HTML_CLASSES.link_selected)
            items.append(self.make_item(djp, classes))
        return items



class Breadcrumbs(lazycounter):
    '''
    Breadcrumbs for current page
    '''
    
    def __init__(self, djp, min_length = 1):
        self.min_length = min_length
    
    def make_item(self, djp, classes, first):
        parent = djp.parent
        if parent:
            c = {'name':    djp.title,
                 'classes': u' '.join(classes)}
            if not first:
                c['url'] = djp.url
            return c
        
    def _items(self, **kwargs):
        first   = True
        classes = []
        djp     = self.djp
        request = djp.request
        val     = self.make_item(djp,classes,first)
        crumbs  = []
        while val:
            crumbs.insert(0, val)
            first = False
            djp   = djp.parent
            val   = self.make_item(djp, classes, first)
            
        if len(crumbs) < self.min_length:
            return []
        else:
            return crumbs
        
        