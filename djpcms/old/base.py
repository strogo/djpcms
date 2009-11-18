from django.utils.encoding import smart_unicode
from django.db import models

from djpcms.utils.models import TimeStamp
from djpcms.fields import SlugCode

current_app_label = 'djpcms'


class PathList(list):
    def __unicode__(self):
        return u' > '.join([smart_unicode(page) for page in self])
    
