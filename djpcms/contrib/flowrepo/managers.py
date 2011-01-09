"""
Custom managers for Django models registered with the flowapp application.
"""
import re
import unicodedata
from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
from django.utils.dates import MONTHS_3
from django.utils.encoding import force_unicode
from django.db.models import signals

source_interactive = 'INTERACTIVE'


class FlowManager(models.Manager):
    """
    A manager for retrieving flow objects
    """
    def __init__(self):
        super(FlowManager, self).__init__()
        self.models_by_name = {}
    
    def allmodels(self):
        '''QuerySet for all models registered with FlowItem.
        It returns a queryset on ContentTypes
        '''
        ids = []
        for model in self.models_by_name.values():
            ct = ContentType.objects.get_for_model(model)
            ids.append(ct.id)
        return ContentType.objects.filter(pk__in = ids)
    
    def selection(self, user, types = None, visibility = 3, tags = ''):
        if visibility == 3:
            qs = self.filter(visibility = 3)
        else:
            if not isinstance(user,User) or not user.is_authenticated():
                return self.none()
            else:
                qs = self.filter(authors = user, visibility = visibility)
        if types:
            qs = qs.filter(content_type__pk__in = types)
        return qs
        
    def get_for_user(self, user, model = None):
        if not isinstance(user,User) or not user.is_authenticated():
            return self.none()
        else:
            qs = self.filter(authors = user)
            if model:
                qs = qs.filter(content_type=ContentType.objects.get_for_model(model))
            return qs
        
    def public(self, user = None, model = None):
        if not isinstance(user,User) or not user.is_authenticated():
            qs = self.filter(visibility = 3)
        else:
            qs = self.filter(visibility__gte = 2)
        if model and model is not self.model:
            ctype = ContentType.objects.get_for_model(model)
            return qs.filter(content_type = ctype)
        else:
            return qs
    
    def private(self, user, model = None):
        '''
        Private items for user
        '''
        if user and user.is_authenticated():
            qs = self.filter(visibility = 1, authors = user)
            if model:
                ctype = ContentType.objects.get_for_model(model)
                return qs.filter(content_type = ctype)
            else:
                return qs
        else:
            return self.none()
    
    def get_from_instance(self, instance):
        ctype = ContentType.objects.get_for_model(instance)
        try:
            return self.get(content_type = ctype, 
                            object_id = force_unicode(instance._get_pk_val()))
        except models.ObjectDoesNotExist:
            return None
        
    def registerModel(self, model, **kwargs):
        name = model.__name__.lower()
        self.models_by_name[name] = model
        signals.post_save.connect(self.create_or_update, sender=model)
        signals.post_delete.connect(self.delete_underlying, sender=self.model)
        
    def unregisterModel(self, model):
        try:
            signals.post_save.disconnect(self.create_or_update, sender=model)
        except Exception, err:
            return False
        else:
            return True
        
    def clean(self):
        n = 0
        for obj in self.all():
            if obj.object == None:
                n += 1
                obj.delete()
        return n
        
    def get_for_model(self, model):
        """
        Return a QuerySet of only items of a certain type.
        """
        return self.filter(content_type=ContentType.objects.get_for_model(model))
    
    def get_interactive_for_model(self, model):
        return self.get_for_model(model).filter(source = source_interactive)
        
    def get_last_update_of_model(self, model, interactive = None, **kwargs):
        """
        Return the last time a given model's items were updated. Returns the
        epoch if the items were never updated.
        """
        qs = self.get_for_model(model)
        if kwargs:
            qs = qs.filter(**kwargs)
        if interactive == True:
            qs = qs.filter(source = source_interactive)
        elif interactive == False:
            qs = qs.exclude(source = source_interactive)
        try:
            return qs.order_by('-timestamp')[0].timestamp
        except IndexError:
            return datetime.fromtimestamp(0)

    def delete_underlying(self, instance, **kwargs):
        try:
            instance.object.delete()
        except:
            pass
        
    def create_or_update(self,
                         instance,
                         user = None,
                         source = None,
                         source_id = None,
                         tags = u'',
                         allow_comments = None,
                         visibility = None,
                         timestamp = None,
                         url = None,
                         **kwargs):
        ctype = ContentType.objects.get_for_model(instance)
        item, created = self.get_or_create(content_type = ctype,
                                           object_id = force_unicode(instance._get_pk_val()))
        item.tags       = tags or item.tags
        item.visibility = visibility or item.visibility
        
        if source_id:
            item.source_id = source_id
        if allow_comments is not None:
            item.allow_comments = allow_comments
        if user:
            item.authors.add(user)

        if timestamp:
            item.timestamp = timestamp
        if url:
            item.url = url
        item.save(source = source)
        return item


class SlugManager(models.Manager):
    
    def __init__(self):
        super(SlugManager,self).__init__()
        self.__baseurl = None
    
    def relative_url(self, dte, slug):
        return u'%s/' % slug
        #if FLOWREPO_SLUG_UNIQUE:
        #    return u'%s/' % slug
        #else:
        #    if FLOWREPO_DIGIT_MONTH:
        #        return u'%s/%02d/%02d/%s/' % (d.year,d.month,d.day,slug)
        #    else:
        #        month = force_unicode(MONTHS_3.get(dte.month))
        #        return u'%s/%s/%02d/%s/' % (d.year,month,d.day,slug)
        
    def object_url(self, obj):
        return self.relative_url(obj.timestamp, obj.slug)
        
    def unique_slug(self, id, slug, c = 0):
        '''
        Depending on settings. If the slug field is unique or not.
        '''
        if c:
            tryslug = u'%s-%s' % (slug,c)
        else:
            tryslug = slug
             
        try:
            obj = self.get(slug = tryslug)
        except:
            return tryslug
        else:
            if obj.id == id:
                return tryslug
            else:
                return self.unique_slug(id,slug,c+1)
            
            
class RepoManager(SlugManager):
    
    def __init__(self):
        super(RepoManager,self).__init__()
        
    def object_url(self, obj):
        if obj.parent:
            base = self.object_url(obj.parent)
        else:
            base = ''
        return u'%s%s/' % (base,obj.slug)
    