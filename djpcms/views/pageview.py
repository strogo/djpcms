'''
This module define djpcmsview specialization for flatpages called pageview.
A pageview is a view not associated with any model in django but
it is associated with a page (instance of Page)
'''
from djpcms.views.baseview import djpcmsview
from djpcms.views.site import get_view_from_page
from djpcms.html import grid960
from djpcms.utils import lazyattr


def create_view(obj, dbmodel, url = u'/', parent = None):
    '''
    view object constructor
        @param dbmodel: the database model for the Page
        @param args:    list of arguments
        @param output_args:   a list or None
        @param edit:    string (Optional)
    '''
    obj.page      = dbmodel
    obj.editurl   = None
    obj.url       = url                
    return obj


class pageview(djpcmsview):
    
    def __new__(cls, *args, **kwargs):
        return create_view(super(pageview, cls).__new__(cls), *args, **kwargs)

    def __unicode__(self):
        return self.url
    
    def get_url(self, request, *args):
        return self.url
    
    def urlname(self):
        return self.page.href_name
    
    def get_page(self):
        return self.page
    
    def parentview(self, request):
        if self.page.parent:
            return get_view_from_page(request, self.page.parent)
        else:
            return None
        
    def grid960(self):
        #return grid960(self.gridcolumns,self.grid_fixed)
        return grid960()

    def urldisplay(self):
        return self.page.href_name
        
    def has_permission(self, request):
        if self.page.requires_login:
            return request.user.is_authenticated()
        else:
            return True
    