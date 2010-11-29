import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


class Log(models.Model):
    '''A database log entry'''
    datetime = models.DateTimeField(default=datetime.datetime.now)
    level = models.CharField(max_length=128)
    msg = models.TextField()
    source = models.CharField(max_length=128, blank=True)
    host = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User,null=True)
    client = models.CharField(max_length=64,blank=True)

    def abbrev_msg(self, maxlen=500):
        if len(self.msg) > maxlen:
            return u'%s ...' % self.msg[:maxlen]
        return self.msg
    abbrev_msg.short_description = u'abbreviated msg'
    
    class Meta:
        get_latest_by = 'datetime'


