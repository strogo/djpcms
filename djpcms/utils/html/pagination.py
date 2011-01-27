__all__ = ['Paginator']


class Paginator(object):
    '''
    List pagination
    It contains Information about the items displayed and a list of links to
    navigate through the search.
    '''
    
    def __init__(self, request, data = None, per_page = 20, numends = 2, maxentries = 15):
        '''
        @param data:       queryset
        @param page:       page to display
        @param per_page:   number of elements per page
        @param maxentries: Max number of links in the pagination list
        '''
        self.hentries   = max(int(maxentries)/2,2)
        self.numends    = numends
        self.total      = data.count()
        self.per_page   = max(int(per_page),1)
        tp              = self.total/self.per_page
        if self.per_page*tp < self.total:
            tp += 1
        self.pages      = tp
        self.page       = self.pagenumber(request)
        end             = self.page*self.per_page
        start           = end - self.per_page
        end             = min(end,self.total)
        self.qs = data[start:end]
        
    def render(self):
        return self.navigation()
        
    def pagenumber(self, request):
        '''
        Get page information form request
        The page should be stored in the request dictionary
        '''
        self._datadict = d = request.data_dict
        page = 1
        if 'page' in d:
            try:
                page = int(d['page'])
            except:
                pass
        return max(min(page,self.pages),1)
    
    def datadict(self):
        s = '?'
        li = []
        for k,v in self._datadict.items():
            li.append('%s=%s' % (k,urlquote(v)))
        return mark_safe('&'.join(li))
        
    def navigation(self):
        if self.pages == 1:
            return u''
        return u''
        ul   = linklist()
        
        # Left links
        if self.page > 1:
            # page is over half-entries. Insert the left link
            if self.page > self.hentries:
                _pagination_entry(ul, prevend, retdata, '', step, total, cn = 'pagination-left-link')
        
        # Right links
        if self.pages < self.pages:
            p = self.page + 1
            while p <= self.pages:
                self._pagination_entry(ul, p)
                p += 1
        return ul            
    
    def _pagination_entry(self, ul, p, cn = None):
        data['_page'] = p
        en  = p*self.per_page
        st  = en - self.per_page + 1
        en  = min(en,self.total) 
        url = datatourl(url, data)
        title = 'page %s from %s to %s' % (p,st,en)
        ul.addlistitem(c, self.url, title = title, cn = cn)
        