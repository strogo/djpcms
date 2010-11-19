
from django.contrib.auth.models import User
from django.db import models

from djpcms.fields import JSONField


class LinkedAccount(models.Model):
    user     = models.ForeignKey(User, related_name = 'linked_accounts')
    provider = models.CharField(blank = False, max_length = 100)
    data     = JSONField()
    
    def __unicode__(self):
        return self.provider
