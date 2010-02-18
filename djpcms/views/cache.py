from django.core.cache import cache

from djpcms.models import Page


class PageCache(object):
    
    def get_from_url(self, url):
        key = 'pagecache:url:%s' % url
        return self._get_and_cache(key, url = url)
    
    def get_for_application(self, code):
        key = 'pagecache:app:%s' % code
        return self._get_and_cache(key, application = code)
    
    def _get_and_cache(self, key, **kwargs):
        page = cache.get(key,None)
        if page:
            return page
        else:
            try:
                page = Page.objects.sitepage(**kwargs)
                cache.set(key, page)
                return page
            except:
                return None
    
    def get_children(self,page):
        key = 'pagecache:children:%s' % page.url
        children = cache.get(key,None)
        if children == None:
            children = list(page.get_children())
            cache.set(key,children)
        return children


pagecache = PageCache()