'''
Define some application urls templates as example
'''
from django.utils.dates import MONTHS_3
from django.utils.encoding import force_unicode

from djpcms.plugins.application.appsite import ModelApplication
from djpcms.views.appview import SearchApp, ArchiveApp, AppView


class ArchiveApplication(ModelApplication):
    '''
    An application urls wich define a search and archive views
    '''
    search        = ArchiveApp()
    year_archive  = ArchiveApp(regex = '(?P<year>\d{4})',  parent = 'search')
    month_archive = ArchiveApp(regex = '(?P<month>\w{3})', parent = 'year_archive')
    day_archive   = ArchiveApp(regex = '(?P<day>\d{2})',   parent = 'month_archive')
    
    def get_month_value(self, month):
        return force_unicode(MONTHS_3.get(month))
        
    def yearurl(self, request, year, **kwargs):
        view = self.getapp('year_archive')
        if view:
            return view.requestview(request, year = year, **kwargs).get_url()
        
    def monthurl(self, request, year, month, **kwargs):
        view  = self.getapp('month_archive')
        if view:
            month = self.get_month_value(month)
            return view.requestview(request, year = year, month = month, **kwargs).get_url()
        
    def dayurl(self, request, year, month, day, **kwargs):
        view = self.getapp('day_archive')
        if view:
            month = self.get_month_value(month)
            return view.requestview(request, year = year, month = month, day = day, **kwargs).get_url()
        
    
    