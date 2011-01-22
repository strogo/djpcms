from django.utils.dates import MONTHS

from djpcms.utils import force_str
from djpcms.views.appview import SearchView



class ArchiveView(SearchView):
    '''
    Search view with archive subviews
    '''    
    def _date_code(self):
        return self.appmodel.date_code
    
    def content_dict(self, djp):
        c = super(ArchiveView,self).content_dict(djp)
        month = c.get('month',None)
        if month:
            c['month'] = self.appmodel.get_month_number(month)
        year = c.get('year',None)
        day  = c.get('day',None)
        if year:
            c['year'] = int(year)
        if day:
            c['day'] = int(day)
        return c
    
    def appquery(self, djp, **kwargs):
        qs       = super(ArchiveView,self).appquery(djp, **kwargs)
        kwargs   = djp.kwargs
        month    = kwargs.get('month',None)
        day      = kwargs.get('day',None)
        dt       = self._date_code()
        dateargs = {}
        if 'year' in kwargs:
            dateargs['%s__year' % dt] = int(kwargs['year'])
        
        if month:
            month = self.appmodel.get_month_number(month)
            if month:
                dateargs['%s__month' % dt] = month
    
        if day:
            dateargs['%s__day' % dt] = int(day)
            
        #qs = self.basequery(request, **kwargs)
        if dateargs:
            return qs.filter(**dateargs)
        else:
            return qs


class DayArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(DayArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        return djp.getdata('day')
    
    
class MonthArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(MonthArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        m = self.appmodel.get_month_number(djp.getdata('month'))
        return force_str(MONTHS[m])
                                          
    
class YearArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(YearArchiveView,self).__init__(*args,**kwargs)
    def title(self, djp):
        return djp.getdata('year')