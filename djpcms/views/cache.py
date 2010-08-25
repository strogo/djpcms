from django.core.cache import cache
from django.contrib.sites.models import Site
from django.http import Http404

from djpcms.models import Page


class PageCache(object):
    
    def __init__(self):
        self._domain = None
        self.applications_url = None
        
    def clear(self, request):
        cache.clear()
        request.session['application-urls-built'] = 0
        
    @property
    def domain(self):
        if not self._domain:
            site = Site.objects.get_current()
            self._domain = site.domain
        return self._domain
    
    def idkey(self, id):
        return '%s:pagecache:id:%s' % (self.domain,id)
    def appkey(self, code):
        return '%s:pagecache:app:%s' % (self.domain,code)
    def urlkey(self, url):
        return '%s:pagecache:url:%s' % (self.domain,url)
    
    def build_app_urls(self, request, force = True):
        from djpcms.views import appsite
        b = request.session.get('application-urls-built',0)
        if not self.applications_url or (force and not b):
            self.applications_url = appsite.site.get_urls()
            request.session['application-urls-built'] = 1
        return self.applications_url
    
    def view_from_url(self, request, url):
        page = self.get_from_url(url)
        if page:
            return self.view_from_page(request, page, False)
        else:
            return None
        
    def view_from_page(self, request, page, docache = True):
        from djpcms.views import appsite
        from djpcms.views.baseview import pageview
        force = False
        if docache:
            force = self._set_if_not(self.urlkey(page.url),page)
        if page.application:
            if docache:
                self._set_if_not(self.appkey(page.application),page,force)
            self.build_app_urls(request, False)
            view = appsite.site.getapp(page.application)
            if not view:
                raise Http404
            view.set_page(page)
        else:
            view = pageview(page)
        return view
    
    def get_from_id(self, id):
        key = self.idkey(id)
        page,created = self._get_and_cache(key, pk = id)
        return page
        
    def get_from_url(self, url):
        key = self.urlkey(url)
        page, created = self._get_and_cache(key, url = url)
        if created and page.application:
            key = self.appkey(page.application)
            cache.set(key, page)
        return page
            
    
    def get_for_application(self, code):
        key = self.appkey(code) 
        page, created = self._get_and_cache(key, application = code)
        if created and page.application:
            key = self.urlkey(page.url)
            cache.set(key, page)
        return page
    
    def _get_and_cache(self, key, **kwargs):
        page = cache.get(key,None)
        if page:
            return page, False
        elif page is None:
            try:
                page = Page.objects.sitepage(**kwargs)
                cache.set(key, page)
                return page, True
            except:
                cache.set(key, False)
                return None,False
        else:
            return None,False
        
    def _set_if_not(self, key, page, force = None):
        if force is None:
            p = cache.get(key,None)
            if not p:
                cache.set(key,page)
                return True
        elif force:
            cache.set(key,page)
            return True
        
        return False
    
    def get_children(self,page):
        key = '%s:pagecache:children:%s' % (self.domain,page.url)
        children = cache.get(key,None)
        if children == None:
            children = list(page.children.all().order_by('in_navigation'))
            cache.set(key,children)
            for child in children:
                cache.set(self.idkey(child.id),   child)
                cache.set(self.urlkey(child.url), child)
                if child.application:
                    cache.set(self.appkey(child.application), child)
        return children

    def sitemap(self):
        from djpcms.views import appsite
        key = '%s:pagecache:sitemap' % self.domain
        map = cache.get(key,None)
        if not map:
            pages = Page.objects.sitepages(is_published = True, requires_login = False, insitemap = True)
            map = []
            for page in pages:
                if page.application:
                    try:
                        app = appsite.site.getapp(page.application)
                    except:
                        continue
                    if app.insitemap and app.has_permission():
                        if not app.regex.targs:
                            map.append(page)
                        else:
                            appmodel = getattr(app,'appmodel',None)
                            if appmodel:
                                map.extend(app.sitemapchildren())
                else:
                    map.append(page)
            cache.set(key,map)
        return map

pagecache = PageCache()