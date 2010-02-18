from django.core.cache import cache
from django.contrib.sites.models import Site
from django.http import Http404

from djpcms.models import Page


class PageCache(object):
    
    def __init__(self):
        site = Site.objects.get_current()
        self.domain = site.domain
        self.applications_url = None
    
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
            self.applications_url = appsite.site.urls
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
        return self._get_and_cache(key, pk = id)
        
    def get_from_url(self, url):
        key = self.urlkey(url)
        page = self._get_and_cache(key, url = url)
        if page and page.application:
            key = self.appkey(page.application)
            cache.set(key, page)
        return page
            
    
    def get_for_application(self, code):
        key = self.appkey(code) 
        page = self._get_and_cache(key, application = code)
        if page and page.application:
            key = self.urlkey(page.url)
            cache.set(key, page)
        return page
    
    def _get_and_cache(self, key, **kwargs):
        page = cache.get(key,None)
        if page:
            return page
        elif page is None:
            try:
                page = Page.objects.sitepage(**kwargs)
                cache.set(key, page)
                return page
            except:
                cache.set(key, False)
                return None
        else:
            return None
        
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


pagecache = PageCache()