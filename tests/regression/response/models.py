from django.db import models

class Strategy(models.Model):
    name     = models.CharField(unique = True, max_length = 200)
    description = models.TextField(blank = True)
    
    def __unicode__(self):
        return u'%s' % self.name