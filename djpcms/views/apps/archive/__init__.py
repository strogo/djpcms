'''
Define some application urls templates as example
'''
import copy

from django.template import loader, Context
from django.utils.dates import MONTHS_3, MONTHS_3_REV, WEEKDAYS_ABBR, MONTHS
from django.utils.encoding import force_unicode

from djpcms.views.appsite import ModelApplication
from djpcms.views import appview

__all__ = ['ArchiveApplication']


class ArchiveApplication(ModelApplication):
    '''
    An application urls wich define a search and archive views
    '''
    date_code     = None
    '''The model field name which is used to create time archives. Must be a date or datetime field.'''
    split_days    = False
    search        = appview.ArchiveView(in_navigation = True)
    year_archive  = appview.YearArchiveView(regex = '(?P<year>\d{4})')
    month_archive = appview.MonthArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive')
    day_archive   = appview.DayArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive')
    
    def get_month_value(self, month):
        return force_unicode(MONTHS_3.get(month))

    def get_month_number(self, month):
        try:
            return int(month)
        except:
            return MONTHS_3_REV.get(month,None)
        
    def yearurl(self, request, year, **kwargs):
        view = self.getview('year_archive')
        if view:
            return view(request, year = year, **kwargs).url
        
    def monthurl(self, request, year, month, **kwargs):
        view  = self.getview('month_archive')
        if view:
            month = self.get_month_value(month)
            return view(request, year = year, month = month, **kwargs).url
        
    def dayurl(self, request, year, month, day, **kwargs):
        view = self.getview('day_archive')
        if view:
            month = self.get_month_value(month)
            return view(request, year = year, month = month, day = day, **kwargs).url
        
    def data_generator(self, djp, data):
        '''
        Modify the standard data generation method so that links to date archive are generated
        '''
        request  = djp.request
        prefix   = djp.prefix
        wrapper  = djp.wrapper
        date     = None
    
        for obj in data:
            content = self.object_content(djp, obj)
            dt      = getattr(obj,self.date_code)
            ddate   = dt.date()
            if self.split_days and (not date or date != ddate):
                urlargs = copy.copy(djp.urlargs)
                urlargs.pop('year',None)
                urlargs.pop('month',None)
                urlargs.pop('day',None)
                content['year']  = {'url': self.yearurl(request,dt.year,**urlargs),
                                    'value': dt.year}
                content['month'] = {'url': self.monthurl(request,dt.year,dt.month,**urlargs),
                                    'value': force_unicode(MONTHS[dt.month])}
                content['day']   = {'url': self.dayurl(request,dt.year,dt.month,dt.day,**urlargs),
                                    'value': dt.day}
                content['wday']  = force_unicode(WEEKDAYS_ABBR[dt.weekday()])
                date = ddate
            yield loader.render_to_string(template_name    = self.get_item_template(obj, wrapper),
                                          context_instance = Context(content))
    
    