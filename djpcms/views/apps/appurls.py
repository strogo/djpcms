'''
Define some application urls templates as example
'''
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
    
    def dateurl(self, request, *args, **kwargs):
        '''
        Get urls for different archives
        '''
        if self.num_args_post_date:
            dargs = args[self.num_args_pre_date:-self.num_args_post_date]
        else:
            dargs = args[self.num_args_pre_date:]
        N = len(dargs)
        if N == 1:
            view = self.getapp('year_archive')
        elif N == 2:
            view = self.getapp('month_archive')
        elif N == 3:
            view = self.getapp('day_archive')
        else:
            view = None
        if view:
            return view.get_url(*args)
        
    
    