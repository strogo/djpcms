import time

from django.db import models
from django.contrib.auth.models import User


class DeploySite(models.Model):
    user     = models.ForeignKey(User)
    created  = models.DateTimeField(auto_now_add = True)
    comment  = models.TextField(blank = True)
    
    def __unicode__(self):
        return u'%s' % self.created
    
    class Meta:
        get_latest_by = "created"
        
    def getval(self):
        return int(time.mktime(self.created.timetuple()))