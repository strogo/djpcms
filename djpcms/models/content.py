from django.contrib.auth.models import User
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from djpcms.djutils.models import TimeStampUser
from djpcms.html import htmlPlugin
from djpcms.uploads import upload_function, site_image_storage
from djpcms.markups import markup_choices, MARKUP_HANDLERS, default_markup
from djpcms.settings import *

from base import *


__all__ = ['SiteContent','SiteImage','create_new_content']



class SiteContentManager(models.Manager):
    
    _cache  = {}
    
    def get_from_code(self, code):
        c = code.lower()
        try:
            return self.__class__._cache[c]
        except:
            try:
                obj = SiteContent.objects.get(code = c)
                if CACHE_VIEW_OBJECTS:
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


class SiteContent(models.Model):
    last_modified = models.DateTimeField(auto_now = True, editable = False)
    user_last     = models.ForeignKey(User, null = True, blank = True)
    code          = SlugCode(max_length = 64,
                             unique     = True,
                             help_text  = _("Unique name for the content. Choose one you like"))
    description   = models.TextField(blank = True)
    body          = models.TextField(_('body'),blank=True)
    markup        = models.CharField(max_length = 3,
                                     choices = markup_choices(),
                                     default = default_markup,
                                     null = False)
    
    objects = SiteContentManager()
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        app_label = current_app_label
        ordering  = ('code',)
    
    def htmlbody(self):
        text = self.body
        if not text:
            html = u''
        mkp = MARKUP_HANDLERS.get(self.markup,None)
        if mkp:
            handler = mkp.get('handler')
            html = force_unicode(handler(text))
        return mark_safe(html)
    
    def update(self, user = None, body = ''):
        self.body = body
        user_last = None
        if user and user.is_authenticated():
            user_last = user
        self.user_last = user_last
        self.save()
        
    
class SiteImage(models.Model):
    code        = SlugCode(max_length = 64,
                           unique = True,
                           help_text = _("Unique name for the image. Choose one you like"))
    image       = models.ImageField(upload_to = upload_function, storage = site_image_storage())
    path        = models.CharField(max_length=200,
                                   blank = True,
                                   help_text = _("Optional, relative path in file storage"))
    description = models.TextField(blank = True)
    url         = models.URLField(blank = True)
    
    class Meta:
        app_label = current_app_label
        
    def __unicode__(self):
        return u'%s' % self.image



def create_new_content(user = None, **kwargs):
    user_last = None
    if user and user.is_authenticated():
        user_last = user
    ct = SiteContent(user_last = user_last, **kwargs)
    ct.save()
    return ct