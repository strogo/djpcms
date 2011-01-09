from djpcms.views import appsite, appview



class SitemapView(appview.SearchView):
    pass



class SitemapAdmin(appsite.ModelApplication):
    home = SitemapView()
    
    class Media:
        js = ['/djpcms/jstree/jquery.tree.js']
    
    