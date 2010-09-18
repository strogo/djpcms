import time

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


class DeploySite(models.Model):
    site     = models.ForeignKey(Site)
    user     = models.ForeignKey(User)
    created  = models.DateTimeField(auto_now_add = True)
    comment  = models.TextField(blank = True)
    
    def __unicode__(self):
        return u'%s' % self.created
    
    class Meta:
        get_latest_by = "created"
        
    def getval(self):
        return int(time.mktime(self.created.timetuple()))