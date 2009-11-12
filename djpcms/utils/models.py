
from django.db import models
from django.contrib.auth.models import User


class TimeStamp(models.Model):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
        

class TimeStampUser(TimeStamp):
    #created_by        = models.ForeignKey(User, null = True, blank = True, editable = False, related_name = 'model_created')
    #last_modified_by  = models.ForeignKey(User, null = True, blank = True, editable = False)

    class Meta:
        abstract = True