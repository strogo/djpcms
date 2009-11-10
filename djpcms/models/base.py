from django.utils.encoding import smart_unicode
from django.db import models

from djpcms.djutils.models import TimeStamp
from djpcms.djutils.fields import SlugCode

current_app_label = 'djpcms'


class PathList(list):
    def __unicode__(self):
        return u' > '.join([smart_unicode(page) for page in self])
    
    
application_types = ((u'',      u'----------'),
                     (u'search',u'search'),
                     (u'add',   u'add'),
                     (u'edit',  u'edit'),
                     (u'view',  u'view'))
