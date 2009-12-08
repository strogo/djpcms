'''
Define some application urls templates as example
'''
import copy

from django.template import loader, Context
from django.utils.dates import MONTHS_3, WEEKDAYS_ABBR, MONTHS
from django.utils.encoding import force_unicode

from djpcms.views.appsite.options import ModelApplication
from djpcms.views.appview import ArchiveView

__all__ = ['ArchiveApplication']


class ArchiveApplication(ModelApplication):
    '''
    An application urls wich define a search and archive views
    '''
    split_days    = False
    search        = ArchiveView()
    year_archive  = ArchiveView(regex = '(?P<year>\d{4})',  parent = 'search')
    month_archive = ArchiveView(regex = '(?P<month>\w{3})', parent = 'year_archive')
    day_archive   = ArchiveView(regex = '(?P<day>\d{2})',   parent = 'month_archive')
    
    def get_month_value(self, month):
        return force_unicode(MONTHS_3.get(month))
        
    def yearurl(self, request, year, **kwargs):
        view = self.getapp('year_archive')
        if view:
            return view.requestview(request, year = year, **kwargs).url
        
    def monthurl(self, request, year, month, **kwargs):
        view  = self.getapp('month_archive')
        if view:
            month = self.get_month_value(month)
            return view.requestview(request, year = year, month = month, **kwargs).url
        
    def dayurl(self, request, year, month, day, **kwargs):
        view = self.getapp('day_archive')
        if view:
            month = self.get_month_value(month)
            return view.requestview(request, year = year, month = month, day = day, **kwargs).url
        
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
    
    