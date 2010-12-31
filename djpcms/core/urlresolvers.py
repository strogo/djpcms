
def get_resolver(regex, urls):
    from django.core import urlresolvers
    return urlresolvers.RegexURLResolver(regex,urls)
    


class SiteResolver(object):
    
    def urls(self):
        raise NotImplemented
    
    def resolve(self, rurl):
        resolver = get_resolver(r'^/', self.urls())
        site, rurl, kwargs = resolver.resolve(rurl)
        return site
        
    def __call__(self, request, rurl):
        from djpcms.views.baseview import djpcmsview
        elem = self
        regex = r'^/'
        while True:
            resolver = get_resolver(regex, elem.urls())
            elem, rurl, kwargs = resolver.resolve(rurl)
            if isinstance(elem,djpcmsview):
                return elem, rurl, kwargs
            else:
                regex = r'^'
                rurl = rurl[0]
        
        