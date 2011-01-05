import datetime
from copy import copy

from django.conf.urls.defaults import patterns
from django.contrib.sitemaps import Sitemap

from djpcms import sites
from djpcms.views import appsite
from djpcms.views.cache import pagecache


def urliterable(urls):
    if isinstance(urls,list):
        return True
    else:
        return False
    

class DjpUrl(object):
    
    def __init__(self):
        self._pre = []
        self._after = []
        
    def __str__(self):
        return str(self._pre)
    
    def append(self, url):
        if url:
            if not urliterable(url):
                url = [url]
            self._pre.extend(url)
        
    def after(self, url):
        if url:
            if not urliterable(url):
                url = [url]
            self._after.extend(url)
        
    def all(self):
        lurl = copy(self._pre)
        lurl.append((r'(.*)', sites.request_handler))
        lurl.extend(self._after)
        return tuple(lurl)
    
    def patterns(self):
        return patterns('', *self.all())
    

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