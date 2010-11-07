from datetime import datetime

from django.db import models
from django.utils import text
from django.utils.encoding import force_unicode, smart_unicode
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group, AnonymousUser

from tagging.fields import TagField

from djpcms.fields import JSONField
from flowrepo import markups
from flowrepo.managers import FlowManager, SlugManager, RepoManager 
from flowrepo.managers import slugify, source_interactive
from flowrepo.storage import uploader, storage_manager
from flowrepo.utils import encrypt, decrypt, nicetimedelta
from flowrepo import settings

report_type = (
        (1, 'blog'),
        (2, 'content'),
        (3, 'wiki'),
        (4, 'article')
        )

visibility_choices = (
        (0, _('Hidden')),              
        (1, _('Private')),          # In draft, availoable to view only to authors
        (2, _('Authenticated')),    # authenitaced users only
        (3, _('Public')),
    )


class FlowItemBase(models.Model):
    
    class Meta:
        abstract = True
    
    def flowitem(self):
        return FlowItem.objects.get_from_instance(self)
    
    def update_related(self, qs):
        item = self.flowitem()
        if item:
            item._update_related(qs)    


class FlowItem(FlowItemBase):
    '''A general pointer to models. Ultra Denormalised for efficiency.
    '''
    content_type = models.ForeignKey(ContentType, editable = False)
    object_id    = models.TextField(editable = False)
    object       = generic.GenericForeignKey('content_type', 'object_id')
    authors      = models.ManyToManyField(User, blank = True, null = True)
    groups       = models.ManyToManyField(Group, blank = True, null = True)
    
    # "Standard" metadata each object provides.
    last_modified   = models.DateTimeField(auto_now = True, editable = False)
    timestamp       = models.DateTimeField()
    url             = models.CharField(blank=True, max_length=1000)
    visibility      = models.IntegerField(choices=visibility_choices, default=3)
    tags            = TagField(max_length=2500, blank = True)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    
    # Metadata about where the object "came from"
    source       = models.CharField(max_length=100, blank=True, editable = False)
    source_id    = models.TextField(blank=True, editable = False)
    
    # Denormalized object for performance in search
    name         = models.CharField(max_length = 255)
    description  = models.TextField(blank=True)
    object_str   = models.TextField(blank=True, editable = False)
    
    markup      = models.CharField(max_length=3,
                                   choices=markups.choices(),
                                   default=markups.default(),
                                   editable=settings.FLOWREPO_SHOW_MARKUP_CHOICE,
                                   blank=True)
    
    objects      = FlowManager()
    
    class Meta:
        ordering        = ['-timestamp']
        unique_together = [("content_type", "object_id")]
        get_latest_by   = 'timestamp'
        
    def __unicode__(self):
        return self.url or self.name or self.object_str 
        
    def flowitem(self):
        return self
    
    def can_user_view(self, user = None):
        if user and user.is_authenticated():
            if self.has_author(user):
                return True
            else:
                return self.visibility >= 2
        else:
            return self.visibility >= 3
        
    def relativestamp(self):
        '''
        Get a human redable string representing the posting time
        Returns:
          A human readable string representing the posting time
        '''
        return nicetimedelta(datetime.now(),self.timestamp)
    relativestamp = property(relativestamp, doc='Get a human readable string representing'
                                                'the posting time')
        
    def has_author(self, user):
        return user in self.authors.all()
    
    def follow(self, item):
        re = FlowRelated.objects.filter(related = item)
        if not re:
            re = FlowRelated(item = self, related = item)
            re.save()
        else:
            re = re[0]
        return re
    
    def filter_for_model(self, model):
        ct = ContentType.objects.get_for_model(model)
        return self.filter(content_type = ct)
    
    def create_for_object(self, item, obj):
        ct = ContentType.objects.get_for_model(obj)
        m = self.model(content_type = ct, object_id = obj.pk, item = item)
        m.save()
        return m

    
    def save(self, force_insert=False, force_update=False, source = None, using=None):
        instance    = self.object
        mkp         = markups.get(self.markup)
        
        try:
            repr = instance.representation(mkp)
        except:
            repr = smart_unicode(instance)
        
        try:
            short_repr = instance.short_representation(mkp)
        except:
            short_repr = self.description
            
        self.object_str  = repr
        self.name        = getattr(instance,'name',self.name)
        self.description = short_repr
        self.url         = getattr(instance,'url',self.url)
        timestamp        = self.timestamp
        if not source:
            self.source = source_interactive
        else:
            self.source = source
        if not timestamp:
            timestamp = datetime.now()
        self.timestamp  = timestamp
        super(FlowItem, self).save(force_insert, force_update)
        
    def niceauthors(self, sep = ', ', intro = 'by '):
        authors = self.authors.all()
        alist = []
        for a in authors:
            fn = a.get_full_name() or a.username
            alist.append(fn)
        return '%s%s' % (intro,sep.join(alist))
    
    def _update_related(self, qs):
        '''
        qs must be an iterable
        '''
        for obj in qs:
            FlowRelated.objects.create_for_object(self, obj)


class CategoryType(FlowItemBase):
    name        = models.CharField(unique = True, max_length = 255)
    
    def __unicode__(self):
        return self.name
    

class SlugBase(FlowItemBase):
    '''
    Provides for a name field and a unique slug field
    '''
    name            = models.CharField(_('title'),max_length=255)
    slug            = models.SlugField(_('slug'),
                                       max_length=260,
                                       help_text= _('Unique code. Autogenerated if not provided'),
                                       blank  = True,
                                       unique = True)
    
    objects         = SlugManager()
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return self.name
        
    def save(self, **kwargs):
        '''
        In this case implicit is better than explicit. Django is changing in this function
        '''
        model = self.__class__
        slug = self.slug
        if not slug:
            slug = slugify(self.name)
        self.slug = model.objects.unique_slug(self.id, slug.lower())
        super(SlugBase,self).save(**kwargs)
        
    def _tohtml(self, text, mkp):
        if not text:
            return u''
        
        if mkp:
            handler = mkp.get('handler')
            text = handler(text)
        
        return mark_safe(text)
        

class Category(SlugBase):
    type        = models.ForeignKey(CategoryType)
    body        = models.TextField(_('body'),blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def tohtml(self):
        return self._tohtml(self.body)



class Report(SlugBase):
    description = models.TextField(_('abstract'),blank=True)
    body        = models.TextField(_('body'),blank=True)
    #markup      = models.CharField(max_length=3,
    #                               choices=markups.choices(),
    #                               default=markups.default(),
    #                               editable=settings.FLOWREPO_SHOW_MARKUP_CHOICE,
    #                               blank=True)
    parent      = models.ForeignKey('self',
                                    null = True,
                                    blank = True,
                                    related_name = 'children')
    
    objects = RepoManager()
        
    def get_absolute_url(self):
        return self.__class__.objects.object_url(self)
    url = property(get_absolute_url)
    
    def representation(self, mkp):
        return self._tohtml(self.body, mkp)
    
    def short_representation(self, mkp):
        return self._tohtml(self.description, mkp)


class Bookmark(SlugBase):
    '''
    A bookmark
    '''
    url           = models.URLField(max_length=1000)
    extended      = models.TextField(blank=True)
    thumbnail     = models.ImageField(upload_to = uploader, blank=True)
    thumbnail_url = models.URLField(blank=True, verify_exists=False, max_length=1000)
    
    def representation(self):
        return self.extended
        

class UploadBase(SlugBase):
    description = models.TextField(blank = True)
    elem_url    = models.URLField(_('Remote URL'),
                                  blank = True,
                                  verify_exists=False, max_length=1000)
    
    class Meta:
        abstract = True
    
    def mimetype(self):
        elem = self.elem
        return 'pdf'
    
    def short_representation(self):
        return self._tohtml(self.description)
        
    def __get_absolute_url(self):
        if self.elem_url:
            return self.elem_url
        else:
            try:
                return self.elem.url
            except:
                return ''
    url = property(__get_absolute_url)
            
            
class Image(UploadBase):
    elem        = models.ImageField(_('image'),
                                    help_text = _('upload an image. If set remote url is ignored'),
                                    blank = True,
                                    upload_to = uploader,
                                    storage = storage_manager('IMAGE'))


class Gallery(SlugBase):
    
    class Meta:
        verbose_name_plural = 'Galleries'
    
class GalleryImage(models.Model):
    image = models.ForeignKey(Image)
    gallery = models.ForeignKey(Gallery, related_name = 'images')
    order = models.IntegerField(default = 1)
    
    class Meta:
        ordering = ('order',)
        
    def __get_url(self):
        return self.image.url
    url = property(__get_url)
    

class Attachment(UploadBase):
    elem        = models.FileField(_('attachment'),
                                   help_text = _('upload an attachment. If set remote url is ignored'),
                                   blank = True,
                                   upload_to = uploader,
                                   storage = storage_manager('ATTACHMENT'))
    
class Message(models.Model):
    """
    A message, status update, or "tweet".
    """
    message = models.TextField()
    url     = models.URLField(blank = True)
    links   = models.ManyToManyField('ContentLink',blank=True,null=True)
    
    def __unicode__(self):
        mkp = markups.get('crl')
        if mkp:
            handler = mkp.get('handler')
            try:
                return handler(smart_unicode(self.message))
            except:
                return self.message
        else:
            return self.message
    
    
class ContentLink(models.Model):
    url = models.URLField()
    identifier = models.CharField(max_length=128)

    def __unicode__(self):
        return self.identifier
    

class FlowRelated(models.Model):
    """
    Holds the relationship between a a FlowItem and other FlowItems
    """
    item         = models.ForeignKey(FlowItem, related_name='following')
    related      = models.ForeignKey(FlowItem, related_name='followers')
  
    class Meta:
        unique_together = ('item','related')
        
    def __unicode__(self):
        return '%s -> %s' % (self.item,self.related)
    


class WebAccount(models.Model):
    '''
    This model can be used to store log-in information
    for a web-account. The log-in details such as username, password pin number etc...
    are encrypted and saved into the database as an encrypted string
    '''
    user   = models.ForeignKey(User)
    name   = models.CharField(blank = False, max_length = 100)
    url    = models.URLField(max_length=1000)
    e_data = models.TextField(blank = True, verbose_name = 'encrypted data')
    tags   = TagField(max_length=2500)

    class Meta:
        unique_together = ('name','user')
        
    def __unicode__(self):
        return u'%s - %s' % (self.name, self.url)

    def encrypted_property(name):
        return property(get_value(name), set_value(name))
    
    def __get_data(self):
        if self.e_data:
            return decrypt(self.e_data)
        else:
            return u''
    def __set_data(self, value):
        if value:
            svalue = encrypt(value)
        else:
            svalue = u''
        self.e_data = svalue
    data   = property(__get_data,__set_data)
    
    
class LinkedAccount(models.Model):
    user     = models.ForeignKey(User, related_name = 'linked_accounts')
    provider = models.CharField(blank = False, max_length = 100)
    data     = JSONField()


FlowItem.objects.registerModel(Report,add = 'write')
FlowItem.objects.registerModel(Bookmark)
FlowItem.objects.registerModel(Message)
FlowItem.objects.registerModel(Image, add = 'upload')
FlowItem.objects.registerModel(Gallery, add = 'create')
FlowItem.objects.registerModel(Attachment, add = 'upload')
FlowItem.objects.registerModel(Category)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^tagging\.fields\.TagField"])
except:
    pass
