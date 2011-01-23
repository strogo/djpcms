from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from djpcms.utils import force_str
from djpcms.core.permissions import get_view_permission


class ContentBlockError(Exception):
    pass
    

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
    
    def create_for_site(self, site = None, **kwargs):
        site = site or Site.objects.get_current()
        page = self.model(site=site,**kwargs)
        page.save()
        return page
    
    def sitepages(self, **kwargs):
        site = Site.objects.get_current()
        return self.filter(site = site, **kwargs)
    
    def sitepage(self, **kwargs):
        site = Site.objects.get_current()
        try:
            return self.get(site = site, **kwargs)
        except ObjectDoesNotExist:
            if kwargs.get('url',None) == '/':
                page = self.model(site = site, url = '/')
                page.save()
                return page
            else:
                raise

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

    
    
class BlockContentManager(models.Manager):
    '''
    BlockContent manager
    '''
    def for_page_block(self, page, block):
        '''
        Get contentblocks for a given page and block
        @param page: instance of a page model
        @param block: integer indicating the block number
        @return: a queryset  
        '''
        blockcontents = list(self.filter(page = page, block = block))
        create = False
        pos = None

        # No contents, create an empty one
        if not blockcontents:
            create = True
            pos    = 0
        # Last content has a plugin. Add another block
        elif blockcontents[-1].plugin_name:
            create = True
            pos = blockcontents[-1].position + 1
            
        if create:
            bc =self.model(page = page, block = block, position = pos)
            bc.save()
            
        return self.filter(page = page, block = block)
    
    def plugin_content_from_name(self, name):
        global _plugin_dictionary
        model = _plugin_dictionary.get(name,None)
        if model:
            return ContentType.objects.get_for_model(model)
        else:
            return None
        
    def delete_and_sort(self, instance):
        '''
        This function delete from database a blockcontent instance.
        Actually it only deletes it if there are more than one contents in the block
        otherwise it only delete the embedded plugin
        @param instance: instance of BlockContent 
        '''
        if instance and instance.plugin:
            blockcontents = self.for_page_block(instance.page, instance.block)
            
            if blockcontents.count() == 1:
                b = blockcontents[0]
                if b != instance:
                    raise ContentBlockError("Critical error in deleting contentblock")
                b.delete_plugin()
            elif blockcontents.count() > 1:
                pos = 0
                for b in blockcontents:
                    if b == instance:
                        b.delete()
                        continue
                    if b.position != pos:
                        b.position = pos
                        b.save()
                    pos += 1
            else:
                raise ContentBlockError("Critical error in deleting contentblock. No Contentblock found")
            
            return True
        else:
            return False
        

class SiteContentManager(models.Manager):
    CACHE_VIEW_OBJECTS = False
    
    _cache  = {}
    
    def get_from_code(self, code):
        c = code.lower()
        try:
            return self.__class__._cache[c]
        except:
            try:
                obj = self.get(code = c)
                if self.CACHE_VIEW_OBJECTS:
                    self.__class__._cache[c] = obj
                return obj
            except:
                pass
            
    def get_from_codes(self, codes):
        objs = []
        for code in codes:
            obj = self.get_from_code(code)
            if obj:
                objs.append(obj)
        return objs        
    
    def clear_cache(self):
        self.__class__._cache = {}



class PermissionManager(models.Manager):
    
    def for_object(self, obj, code):
        pe = self._get_permission(obj, code)
        if not pe:
            return None
        return self.filter(content_id = obj.pk, permission = pe)
        
    def set_view_permission(self, obj, users = None, groups = None):
        code = get_view_permission(obj)
        pe = self._get_permission(obj, code, True)
        self.filter(content_id = obj.pk, permission = pe).delete()
        self._add_permission(pe, obj, users, groups)
        
    def add_view_permission(self, obj, users = None, groups = None):
        '''Add a view permission to *groups* and/or *users* for object *obj*'''
        code = get_view_permission(obj)
        pe = self._get_permission(obj, code, True)
        self._add_permission(pt,obj,users,groups)
        
    def _get_permission(self, obj, code, create = False):
        ct = ContentType.objects.get_for_model(obj)
        pe = Permission.objects.filter(codename = code, content_type = ct)
        if pe:
            pe = pe[0]
        elif create:
            pe = Permission(codename = code, content_type = ct, name = 'Can view %s' % force_str(obj._meta.verbose_name))
            pe.save()
        return pe
        
    def _add_permission(self,pe,obj,users,groups):
        ct = pe.content_type
        if groups:
            for group in groups:
                op = self.model(group = group, content_type = ct,
                                content_id = obj.pk, permission = pe)
                op.save()
        if users:
            for user in users:
                op = self.model(user = user, content_type = ct,
                                content_id = obj.pk, permission = pe)
                op.save()
        