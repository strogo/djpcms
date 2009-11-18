from django.contrib.sites.models import Site
from django.db import models

from djpcms.settings import DEFAULT_TEMPLATE_NAME

from page import PageBase
from base import *

__all__ = ['AppPage']

class AppPageManager(models.Manager):
    
    def sitepage(self, **kwargs):
        site = Site.objects.get_current()
        return self.get(site = site, **kwargs)
    
    def sitepages(self, **kwargs):
        site = Site.objects.get_current()
        return self.filter(site = site, **kwargs)
    
    def get_for_code(self, code):
        return self.sitepage(code = code)

class AppPage(PageBase):
    code = models.CharField(max_length = 100, blank = False, verbose_name='application')
    
    objects = AppPageManager()
    
    class Meta:
        app_label = current_app_label
        unique_together = ('site','code')
    
    def get_template(self):
        '''
        HTML template for the page
        if not specified we get the template of the parent page
        '''
        if not self.template:
            return DEFAULT_TEMPLATE_NAME
        else:
            return self.template
    get_template.verbose_name = 'template file'
    
    def __unicode__(self):
        return u'%s' % self.code
