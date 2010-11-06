'''
Utility module for creating a navigation list
'''
from djpcms.template import loader
from djpcms.utils import lazyattr


class lazycounter(object):
    '''A lazy view counter used to build navigations type iterators
    '''
    def __new__(cls, djp, **kwargs):
        obj = super(lazycounter, cls).__new__(cls)
        obj.djp     = djp
        obj.classes = kwargs.pop('classes',None)
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
    '''A navigator for the web site
    '''
    def __init__(self, *args, **kwargs):
        self.soft    = self.kwargs.pop('soft',False)
        self.url     = self.kwargs.pop('url','')
        self.name    = self.kwargs.pop('name','')
        self.levels  = self.kwargs.pop('levels',1)
        self.mylevel = self.kwargs.pop('mylevel',0)
        self.liclass = self.kwargs.pop('liclass',None)
        
    def make_item(self, djp, classes):
        return Navigator(djp,
                         levels = self.levels,
                         mylevel = self.mylevel+1,
                         liclass = classes,
                         url  = djp.url,
                         name = djp.linkname,
                         soft = self.soft,
                         **self.kwargs)
    
    def buildselects(self, djp, urlselects):
        if self.soft and djp.is_soft():
            return djp
        parent = djp.parent
        if parent:
            try:
                url = djp.url
                if url:
                    urlselects.append(url)
            except:
                pass
            return self.buildselects(parent, urlselects)
        return djp
        
    def _items(self, urlselects = None, secondary_after = 100, **kwargs):
        djp = self.djp
        css = djp.css
        if urlselects is None:
            urlselects = []
            djp = self.buildselects(djp,urlselects)
            self.kwargs['urlselects'] = urlselects
        scn        = css.secondary_in_list
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
                classes.append(css.link_selected)
            items.append(self.make_item(djp, u' '.join(classes)))
        return items

    def render(self):
        if self.mylevel <= self.levels:
            return loader.render_to_string('djpcms/bits/navitem.html', {'navigator': self})
        else:
            return u''         


class Breadcrumbs(lazycounter):
    '''
    Breadcrumbs for current page
    '''
    
    def __init__(self, *args, **kwargs):
        self.min_length = self.kwargs.pop('min_length',1)
    
    def make_item(self, djp, classes, first):
        parent = djp.parent
        if parent:
            c = {'name':    djp.title,
                 'classes': u' '.join(classes)}
            if not first:
                try:
                    c['url'] = djp.url
                except:
                    pass
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
        
        