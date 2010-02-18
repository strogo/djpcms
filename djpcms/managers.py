from django.db import models
from django.contrib.sites.models import Site

    

class PageManager(models.Manager):
    '''
    Page manager
    '''    
    def hierarchy(self, parent=None):
        if parent:
            filter = self.filter(parent=parent)
        else:
            try:
                root = self.root()
            except RootPageDoesNotExist:
                return []
            return [(root, self.hierarchy(root))]
        return [(page, self.hierarchy(page)) for page in filter]
    
    def applications(self):
        return self.sitepages().exclude(app_type = u'')
    
    def sitepages(self, **kwargs):
        site = Site.objects.get_current()
        return self.filter(site = site, **kwargs)
    
    def sitepage(self, **kwargs):
        site = Site.objects.get_current()
        return self.get(site = site, **kwargs)

    def clear_cache(self):
        self.__class__._cache.clear()
        
    def root(self, site):
        f = self.filter(level=0, site = site)
        if f:
            return f[0]
        else:
            return None
    
    def root_for_site(self):
        current_site = Site.objects.get_current()
        return self.root(current_site)
        
    def flat_pages(self, **kwargs):
        return self.filter(application = '', **kwargs)
    
    def get_flat_page(self, url, site):
        return self.get(application = '', url = url, site = site)
    
    def get_flat_page_for_site(self, url):
        current_site = Site.objects.get_current()
        return self.get_flat_page(url, current_site)
    
    def get_for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type = ct)

    def published(self):
        try:
            user_logged_in = get_current_user().is_authenticated()
        except:
            user_logged_in = False
        if not user_logged_in:
            qs = self.exclude(requires_login=True)
        else:
            qs = self
        return qs.filter(
                           Q(is_published=True),
                           Q(start_publish_date__lte=datetime.datetime.now()) | Q(start_publish_date__isnull=True), 
                           Q(end_publish_date__gte=datetime.datetime.now()) | Q(end_publish_date__isnull=True),
                           )