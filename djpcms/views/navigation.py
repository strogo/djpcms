'''
Utility module for creating a navigation list
'''

from djpcms.settings import HTML_CLASSES
from djpcms.html import linklist
from djpcms.utils import lazyattr
from djpcms.views.site import get_view_from_page
from djpcms.models import Page


def get_children(request, view):
    from djpcms.plugins.application import appsite
    views = []
    page  = view.get_page()
    
    if isinstance(page,Page):
        children = page.get_children()
        for child in children:
            try:
                v = get_view_from_page(request, child)
            except Exception, e:
                continue
            if v.has_permission(request):
                views.append(v)
                
        url = page.absolute_url
        appchildren = appsite.site.parent_pages.get(url,None)
        
        if appchildren:
            # Found application pages, deal with them
            app_nav = []
            for app in appchildren:
                if app.in_navigation and app.root_application:
                    views.append(app.root_application)
    else:
        for app in view.appmodel.applications.values():
            if app.in_navigation and app.parent == view:
                views.append(app)
    
    return views
    


class default_navigation_constructor(object):

    def __init__(self, request, view, nav_func, children):
        self.request = request
        self.view = view
        self.nav_func = nav_func
        self.children = children
        
    @lazyattr
    def get_navigator(self):
        view       = self.view
        parentview = view.parentview(self.request)
        children   = self.children
        if parentview:
            if children:
                children.append(view)
            else:
                children = [view]
            func = getattr(parentview, self.nav_func)
            return func(self.request, children = children)
        else:
            return lazynavigator(self.request, view, urlselects = children)

    def count(self):
        nav = self.get_navigator()
        return nav.count()
    
    def elems(self):
        return self.get_navigator().elems()



class lazynavigator(object):
    
    def __init__(self, request, view, **kwargs):
        self.request = request
        self.view    = view
        self.kwargs  = kwargs
        
    @lazyattr
    def get_children(self):
        return get_children(self.request, self.view)
    
    def count(self):
        return len(self.get_children())

    def elems(self):
        return self._get_navigation(**self.kwargs)

    def _get_navigation(self, urlselects = None, secondary_after = 100):
        scn        = HTML_CLASSES.secondary_in_list
        urlselects = urlselects or []
        
        children = self.get_children()
    
        for view in children:
            cl  = view.requestview(self.request)
            url = view.get_url(self.request)
            classes = []
            if cl.in_navigation() > secondary_after:
                classes.append(scn)
            if url in urlselects:
                classes.append(HTML_CLASSES.link_selected)
            yield {'name': cl.urlname(),
                   'url':  url,
                   'classes': u' '.join(classes),
                   'nav':     lazynavigator(self.request,
                                            view, 
                                            urlselects = urlselects,
                                            secondary_after = secondary_after)}
        
