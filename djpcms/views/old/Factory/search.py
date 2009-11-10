"""
Battery included search view for a django model

This interface can be used by views which requires
searching objects of a given django model
"""

import operator
from decimal import Decimal
import time

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.encoding import force_unicode
from django.http import Http404, HttpResponseRedirect
from django.utils.text import smart_split

from djpcms import settings
from djpcms.adminsite import get_admin
from djpcms.views.base import create_view
from djpcms.html import searchform, div, pagination, linklist
from djpcms.html import link, breadcrumbs
from djpcms.ajax import jhtmls


from fchild import childview

__all__ = ['searchview','construct_search']


def construct_search(field_name):
    if field_name.startswith('^'):
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    else:
        return "%s__icontains" % field_name


def isexact(bit):
    if not bit:
        return bit
    N = len(bit)
    Nn = N - 1
    bc = '%s%s' % (bit[0],bit[Nn])
    if bc == '""' or bc == "''":
        return bit[1:Nn]
    else:
        return bit


#def create_search_view(obj, *args, **kwargs): 
#    obj._queryset  = None
#    obj.data_avail = False
#    return obj
#
#def __new__(cls, *args, **kwargs):
#        return create_search_view(super(searchview, cls).__new__(cls, *args, **kwargs))

class searchview(childview):
    '''
    A "battery included" search view for a model.
    It assumes the data (POST or GET) contains a search
    item from which to perform the search.
    
    This view handle an additional filters
    
    baseurl/filtername/filterval1/filterval2/.../.../
    
    The filter is implemented in a view function
        filterprefix_filtername(self, *args)
        where args = (filterval1,filterval2,..)
    '''
    maxdisplay = settings.MAX_SEARCH_DISPLAY
    filterprefix = 'filter'
    search_field_names = None
    
    def get_object(self, args):
        '''
        Override in order to handle filtered search views
        '''
        self.data_avail = False
        self.withfilter = None
        self.urlargs    = None
        if args:
            if len(args) > 1:
                fname = args[0]
                self.urlargs = args[1:]
                f = getattr(self,'%s_%s' % (self.filterprefix,fname))
                if f:
                    self.withfilter = (fname,f)
                else:
                    raise Http404
            else:
                raise Http404
            
    def breadcrumbs(self, msg = ''):
        '''
        Create a a bread crumb list of filters (if available)
        '''
        if not self.withfilter:
            return msg
        else:
            msg = msg or 'home'
            baseurl = self.childurlbase(self._child.code)
            br = breadcrumbs()
            br.addlistitem(msg, url = baseurl)
            
            url  = '%s%s/' % (baseurl,self.withfilter[0])
            
            # loop over arguments
            for t in self.urlargs[:-1]:
                url = '%s%s/' % (url,t)
                br.addlistitem(str(t), url = url)
            br.addlistitem(str(self.urlargs[-1]))
            return br.render()
        
    def get_extra_filters(self, request):
        return None
    
    def searchform(self, request, params):
        '''
        Return the default serchform
        '''
        return searchform(view = self, request = request, method = 'get', data = params)
    
    def filtertitle(self):
        return ''
        
    def view_contents(self, request, params):
        '''
        handle the get view
        '''
        sf = self.searchform(request, params)
        data = None
        results = {'searchform': sf}
        result  = None
        
        # We have a parameters dictionary
        if params:
            if sf.is_valid():
                data = sf.cleaned_data
                for v in data.values():
                    if v:
                        self.data_avail = True
                        break
                result = self._handle_search(request, data, params)
        else:
            result = self._handle_search(request, data, params)
        
        if result:
            results.update(result)
        return results
    
    def _handle_search(self, request, data, params):
        '''
        handle the search by creating the query and performing pagination
        '''
        query  = self.get_query(request, data)
        try:
            N      = query.count()
        except:
            N      = len(query)
        start  = int(params.get('_start',1))
        end    = int(params.get('_end',start + self.maxdisplay - 1))
        rq     = []
            
        # Only one result, go straight to that page
        if N == 1 and not start:
            url = self.factoryurl('view',query[0])
            return HttpResponseRedirect(url)
                
        if N:
            end    = min(end,N)
            for r in query[start-1:end]:
                try:
                    rq.append(self.make_result(request, r))
                except Exception, e:
                    pass
                    
        
        queryres = {'query': rq}
        result = {'searchresults': queryres}
        
        if self.data_avail or self.withfilter:
            queryres.update({'start': start, 'end': end, 'total': N})
            pgs = pagination(url   = self.url,
                             step  = self.maxdisplay,
                             start = start,
                             total = N,
                             data  = params)
            result.update({'pagination': pgs})
        
        return result
    
    def make_result(self, r):
        '''
        This should be implemented by derived classes.
        It returns an html element to append to the result list
        '''
        raise NotImplementedError
        
    def get_basequeryset(self, request):
        '''
        Base query set
        '''
        filters = self.get_extra_filters(request)
        if self.withfilter:
            fun = self.withfilter[1]
            return fun(request, filters)
        elif filters:
            return self.model.objects.filter(**filters)
        elif self.data_avail:
            return QuerySet(self.model)
        else:
            return self.empty_queryset(request)
    
    def empty_queryset(self, request):
        # This function is called when there are no data parameters for search
        # and no filters
        return QuerySet(self.model)
    
    def get_query(self, request, data = None):
        qs = self.get_basequeryset(request)
        if self.data_avail and data:
            return self._input_data_search(request, data, qs)
        else:
            return qs
        
    
    def _input_data_search(self, request, data, qs):
        '''
        This function can be reimplemented by derived classes
        for customizing search.
        By default we perform a text serach
        
        @param request: django request object
        @param data: dictionary of search keys
        @param qs: initial queryset
        @return: a queryset   
        '''
        return self._textsearch(request, data, qs)
        
    def _textsearch(self, request, data, qs):
        '''
        Construct a text query.
        '''
        m     = self.model
        search_string = data.get('search','').lower()
        
        stype = str(data.get('_search','')).lower()
        
        slist = self.search_field_names
        
        if slist is None:
            admin = get_admin(m)
            slist = admin.search_fields
            
        if not slist:
            raise ValueError, 'Model has not search fields available'
        
        if stype in slist:
            slist = (stype,)
        
        #qs    = admin.queryset(self.request)
        bits  = smart_split(search_string)
        #bits  = search_string.split(' ')
        for bit in bits:
            bit = isexact(bit)
            if not bit:
                continue
            or_queries = [Q(**{construct_search(field_name): bit}) for field_name in slist]
            other_qs   = QuerySet(m)
            other_qs.dup_select_related(qs)
            other_qs   = other_qs.filter(reduce(operator.or_, or_queries))
            qs         = qs & other_qs
            
        return qs
        
    def search_result(self, query):
        raise NotImplementedError
 
        