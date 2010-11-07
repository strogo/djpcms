from django.contrib.sitemaps import Sitemap
from models import Report

class ReportSiteMap(Sitemap):
    changefreq = "never"
    priority = 0.5
    
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def items(self):
        return Report.objects.filter(status=2)

    def lastmod(self, obj):
        return obj.last_modified
    
    def location(self, obj):
        return obj.url(self.baseurl)
