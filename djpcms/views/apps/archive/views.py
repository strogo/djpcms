from djpcms.views.appview import SearchView



class ArchiveView(SearchView):
    '''
    Search view with archive subviews
    '''
    def __init__(self, *args, **kwargs):
        super(ArchiveView,self).__init__(*args,**kwargs)
    
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
    
    def appquery(self, request, year = None, month = None, day = None, **kwargs):
        qs       = super(ArchiveView,self).appquery(request, **kwargs)
        dt       = self._date_code()
        dateargs = {}
        if year:
            dateargs['%s__year' % dt] = int(year)
        
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
    def title(self, page, **urlargs):
        return urlargs.get('day',None)
    
    
class MonthArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(MonthArchiveView,self).__init__(*args,**kwargs)
    def title(self, page, **urlargs):
        return urlargs.get('month',None)
    
    
class YearArchiveView(ArchiveView):
    def __init__(self, *args, **kwargs):
        super(YearArchiveView,self).__init__(*args,**kwargs)
    def title(self, page, **urlargs):
        return urlargs.get('year',None)