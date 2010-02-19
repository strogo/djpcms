import datetime

from django.contrib.sitemaps import Sitemap

from djpcms.views import appsite
from djpcms.views.cache import pagecache


class DjpPage(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    
    '''
    Create a sitemap for a djpcms managed site
    '''
    def items(self):
        return pagecache.sitemap()

    def location(self, obj):
        return obj.url
        
    def lastmod(self, obj):
        return obj.last_modified

    
def get_site_maps():
    site = {'flat': DjpPage}
    return site