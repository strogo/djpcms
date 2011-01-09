from copy import deepcopy

from django.core.cache import cache
from django.contrib.sites.models import Site
from django.db.models import signals
from django.http import Http404

from djpcms import sites
from djpcms.models import Page
from djpcms.views import appsite
from djpcms.views.baseview import pageview


class PageCache(object):
    
    def __init__(self):
        self._domain = None
        self.applications_url = None
        
    def clear(self, request = None):
        cache.clear()
        if request:
            self.session(request)['application-urls-built'] = 0
        
    def session(self, request):
        return getattr(request,'session',{})
        
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
        session = self.session(request)
        b = session.get('application-urls-built',0)
        if not self.applications_url or (force and not b):
            self.applications_url = get_urls()
            session['application-urls-built'] = 1
        return self.applications_url
    
    def view_from_url(self, url):
        '''Get a view object given a url'''
        page = self.get_from_url(url)
        if page:
            return self.view_from_page(page, False)
        else:
            return None
        
    def view_from_page(self, page, site = None, docache = True):
        '''Retrive a view instance from a page instance.
If the page is for an application view, site must be provided otherwise
no search will be performed.'''
        force = False
        view = None
        if docache:
            force = self._set_if_not(self.urlkey(page.url),page)
        if page.application_view:
            if site:
                view = site.getapp(page.application_view)
            if not view:
                raise Http404
        else:
            # Flat pages get created each time
            view = pageview(page)
        return view
    
    def get_from_id(self, id):
        key = self.idkey(id)
        page,created = self._get_and_cache(key, pk = id)
        return page
        
    def get_from_url(self, url):
        '''Get a page given a url'''
        key = self.urlkey(url)
        page = cache.get(key,None)
        if page:
            return page
        try:
            page = Page.objects.sitepage(url = url)
            cache.set(key, page)
            return page
        except:
            return None
    
    def get_for_application(self, code):
        '''Return an iterable of pages for a given application view code. Stre them into cache.'''
        key = self.appkey(code)
        pages, created = self._get_and_cache(key, application_view = code)
        if pages and not hasattr(pages,'__iter__'):
            pages = [pages]
        #if created:
        #    for page in pages:
        #        if page.application_view:
        #            key = self.urlkey(page.url)
        #            cache.set(key, page)
        return pages
    
    def _get_and_cache(self, key, **kwargs):
        pages = cache.get(key,None)
        if pages:
            return pages, False
        elif pages is None:
            try:
                pages = Page.objects.sitepage(**kwargs)
                cache.set(key, pages)
                return pages, True
            except:
                pages = Page.objects.sitepages(**kwargs)
                if pages:
                    cache.set(key, pages)
                    return pages, True
                else:
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
        if children is None:
            children = list(page.children.all().order_by('in_navigation'))
            cache.set(key,children)
            for child in children:
                cache.set(self.idkey(child.id),   child)
                cache.set(self.urlkey(child.url), child)
        return children

    def sitemap(self):
        from djpcms.views import appsite
        key = '%s:pagecache:sitemap' % self.domain
        map = cache.get(key,None)
        if not map:
            pages = Page.objects.sitepages(is_published = True, requires_login = False, insitemap = True)
            map = []
            for page in pages:
                if page.application_view:
                    try:
                        app = appsite.site.getapp(page.application_view)
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



def clearcache(*args, **kwargs):
    sites.clearcache()
    
    
signals.post_save.connect(clearcache, sender=Page)
signals.post_delete.connect(clearcache, sender=Page)

