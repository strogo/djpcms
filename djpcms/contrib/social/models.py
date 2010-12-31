from django.db import models

from djpcms.fields import JSONField
from .defaults import User


class LinkedAccount(models.Model):
    '''Stores authentication token and secret key for a linked account'''
    user       = models.ForeignKey(User, related_name = 'linked_accounts')
    tokendate  = models.DateTimeField()
    uid        = models.CharField(max_length=255)
    token      = models.CharField(max_length = 300)
    secret     = models.CharField(max_length = 300)
    provider   = models.CharField(blank = False, max_length = 100)
    data       = JSONField()
    
    def __unicode__(self):
        return self.provider
