from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from tagging.fields import TagField
from abstract import TimeStamp

__all__ = ['Post','markup_choices','report_status_choices']

markup_choices = (
        ('crl', _(u'Creole')),
        ('rst', _(u'reStructuredText')),
        ('txl', _(u'Textile')),
        ('mrk', _(u'Markdown')),
    )

report_status_choices = (
        (1, _('Draft')),
        (2, _('Public')),
    )



class Post(TimeStamp):
    """
    Post model Interface
    """
    title           = models.CharField(_('title'), max_length=200)
    slug            = models.SlugField(_('slug'))
    author          = models.ForeignKey(User, related_name="added_posts")
    body            = models.TextField(_('body'))
    status          = models.IntegerField(_('status'), choices=report_status_choices, default=2)
    allow_comments  = models.BooleanField(_('allow comments'), default=True)
    publish         = models.DateTimeField(_('publish'), default=datetime.now)
    markup          = models.CharField(_(u"Post Content Markup"), max_length=3,
                              choices=markup_choices,
                              null=True, blank=True)
    tags            = TagField('labels')
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ('blog_post', None, {
            'username': self.author.username,
            'year': self.publish.year,
            'month': "%02d" % self.publish.month,
            'slug': self.slug
    })
    get_absolute_url = models.permalink(get_absolute_url)
