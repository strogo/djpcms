from djpcms.utils.func import data2url

from base import htmlbase

__all__ = ['Paginator']


class Paginator(object):
    '''
    List pagination
    It contains Information about the items displayed and a list of links to
    navigate through the search.
    '''
    
    def __init__(self, request, data = None, per_page = 20, maxentries = 15):
        '''
        @param data:       queryset
        @param page:       page to display
        @param per_page:   number of elements per page
        @param maxentries: Max number of links in the pagination list
        '''
        self.hentries   = max(int(maxentries)/2,2)
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
        Get information form request
        '''
        if request.method == 'GET':
            data = dict(request.GET.items())
        else:
            data = dict(request.POST.items())
        page = data.get('page',1)
        return max(min(page,self.pages),1) 
        
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
        
        
    def legacy_stuff(self):
        self.addclass('search-pagination')
        data = data or {}
        wrap = htmlPlugin(tag = 'div').appendTo(self)
        info = htmlPlugin(tag = 'p').appendTo(wrap)
        ul   = linklist().appendTo(wrap)
        ul.withspan = True
        
        infotemplate = infotemplate or 'Display <b>%s</b> - <b>%s</b> of <b>%s</b>' 
        
        hentries = max(int(maxentries/2),2)
        entries  = 2*hentries + 1
        
        st1     = start - 1
        retdata = {}
        for k,v in data.items():
            retdata[k] = v

        leftpages = st1 / step
        startpage = max(leftpages - hentries + 1,1)
        endelem   =(startpage-1)*step
        c         = 0
        
        # Add the left arrow
        if startpage > 1:
            prevend = endelem - step
            _pagination_entry(ul, self.url, prevend, retdata, '', step, total, cn = 'pagination-left-link')
        
        # Add links to the left
        while endelem < st1:
            endelem = _pagination_entry(ul, self.url, endelem, retdata, c+startpage, step, total)
            c += 1
        
        # Add current page without link
        endelem = min(st1 + step,total)
        ul.addlistitem(c+startpage)
        c += 1
        info.append(infotemplate % (start,endelem,total))
        
        # Add links to the right
        while endelem < total and c < entries:
            endelem = _pagination_entry(ul, self.url, endelem, retdata, c+startpage, step, total)
            c += 1
            
        # Add the right arrow
        if endelem < total:
            _pagination_entry(ul, self.url, endelem, retdata, '', step, total, cn = 'pagination-right-link')
