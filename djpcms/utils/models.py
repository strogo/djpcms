from datetime import datetime

from django.db import models


class TimeStamp(models.Model):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

