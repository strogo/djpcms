'''
This module define djpcmsview specialization for flatpages called pageview.
A pageview is a view not associated with any model in django but
it is associated with a page (instance of Page)
'''
from djpcms.views.baseview import djpcmsview
from djpcms.views.site import get_view_from_page
from djpcms.views import appsite


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
    
    def get_url(self, djp, **urlargs):
        return self.url
    
    def get_page(self):
        return self.page
    
    def parentview(self, request):
        if self.page.parent:
            return get_view_from_page(request, self.page.parent)
        else:
            return None
        
    def has_permission(self, request):
        if self.page.requires_login:
            return request.user.is_authenticated()
        else:
            return True
        
    def children(self, request, **kwargs):
        views = {}
        page      = self.get_page()
        pchildren = page.get_children()
        for child in pchildren:
            try:
                v = get_view_from_page(request, child)
            except Exception, e:
                continue
            if v.has_permission(request):
                views[child.in_navigation] = v.requestview(request, **kwargs)
        #
        # Now check for application children
        appchildren = appsite.site.parent_pages.get(self.url,None)
        
        if appchildren:
            for app in appchildren:
                rootview = app.root_application
                if rootview:
                    djp = rootview.requestview(request, **kwargs)
                    nav = djp.in_navigation()
                    views[nav] = djp
        
        views.pop(0,None)
        return views.values()
        
    