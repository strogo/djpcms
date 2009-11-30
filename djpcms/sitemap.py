import datetime

from django.contrib.sitemaps import Sitemap

from djpcms.models import Page
from djpcms.views import appsite


class DjpPage(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    '''
    Create a sitemap for a djpcms managed site
    '''
    def items(self):
        return Page.objects.flat_pages(is_published = True, requires_login = False)

    def location(self, obj):
        return obj.get_absolute_url()
        
    def lastmod(self, obj):
        return obj.last_modified
    


class SitemapApp(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    def __init__(self, appmodel):
        self.appmodel = appmodel
        
    def items(self):
        apps = []
        for app in self.appmodel.applications.values():
            #
            # If application has all open permission it is added, otherwise no
            if app.has_permission():
                if not app.tot_args:
                    apps.append(app)
        return apps
    
    def location(self, obj):
        return obj.get_url(None)
    
    def lastmod(self, obj):
        return datetime.date.today()
    
def get_site_maps():
    site = {'flat': DjpPage}
    for app in appsite.site._registry.values():
        if app.insitemap:
            site[app.name] = SitemapApp(app)
    return site