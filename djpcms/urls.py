from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import *

import djpcms
from djpcms.settings import SERVE_STATIC_FILES, DJPCMS_PLUGINS, DJPCMS_WRAPPERS
from djpcms.views import appsite

#if not settings.DEBUG:
#    handler404 = 'djpcms.views.specials.http404view'
#    handler500 = 'djpcms.views.specials.http500view'

from djpcms.plugins import loadplugins, loadwrappers
    
loadplugins(DJPCMS_PLUGINS)
loadwrappers(DJPCMS_WRAPPERS)
admin.autodiscover()
appsite.load()


# Admin Site
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    try:
        admin_url_prefix = settings.ADMIN_URL_PREFIX
        site_urls  = url(r'^%s(.*)' % admin_url_prefix[1:],    admin.site.root),
    except:
        site_urls  = ()
else:
    site_urls  = ()
    

# MEDIA FILES ONLY IF REQUESTED
if SERVE_STATIC_FILES:
    import djpcms
    import os
    djpcms_media_root = os.path.join(djpcms.__path__[0],'media')
    murl = settings.MEDIA_URL.lstrip("/")
    site_urls += (r'^%sdjpcms/(?P<path>.*)$' % murl,
                  'django.views.static.serve',
                  {'document_root': djpcms_media_root, 'show_indexes': True}
                  ),
    site_urls += (r'^%ssite/(?P<path>.*)$' % murl,
                  'django.views.static.serve',
                  {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
                  ),
                 

# Applications urls
if appsite.site.count():
    site_urls += appsite.site.urls

# The djcms pagination goes as last
site_urls      += ((r'([\w/-]*)', 'djpcms.views.site.handler'),)


