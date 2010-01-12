'''
This module define djpcmsview specialization for flatpages called pageview.
A pageview is a view not associated with any model in django but
it is associated with a page (instance of Page)
'''
from djpcms.utils.func import force_number_insert
from djpcms.views.baseview import djpcmsview
from djpcms.views import appsite


def create_view(obj, dbmodel):
    '''
    view object constructor
        @param dbmodel: the database model for the Page
        @param args:    list of arguments
        @param output_args:   a list or None
        @param edit:    string (Optional)
    '''
    obj.page      = dbmodel
    obj.editurl   = None              
    return obj


class pageview(djpcmsview):
    
    def __new__(cls, *args, **kwargs):
        return create_view(super(pageview, cls).__new__(cls), *args, **kwargs)

    def __unicode__(self):
        return self.page.url
    
    def get_url(self, djp, **urlargs):
        return self.page.url
    
    def get_page(self):
        return self.page
    
    def parentview(self, request):
        if self.page.parent:
            return self.page.parent.object()
        else:
            return None
        
    def has_permission(self, request = None, obj = None):
        if self.page.requires_login:
            if request:
                return request.user.is_authenticated()
            else:
                return False
        else:
            return True
        
    def children(self, request, **kwargs):
        views = []
        page      = self.get_page()
        pchildren = page.get_children()
        
        # First check static childrens
        for child in pchildren:
            try:
                cview = child.object()
            except Exception, e:
                continue
            if cview.has_permission(request):
                djp = cview(request, **kwargs)
                nav = djp.in_navigation()
                if nav:
                    views.append(djp)
        #
        # Now check for application children
        appchildren = appsite.site.parent_pages.get(self.page.url,None)
        
        if appchildren:
            for app in appchildren:
                rootview = app.root_application
                if rootview and rootview.has_permission(request): 
                    djp = rootview.requestview(request, **kwargs)
                    nav = djp.in_navigation()
                    if nav:
                        views.append(djp)
        
        return self.sortviewlist(views)
        
    