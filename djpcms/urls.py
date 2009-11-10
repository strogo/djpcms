from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import include, url

from djpcms.settings import SERVE_STATIC_FILES, CONTENT_INLINE_EDITING, APPLICATION_URL_PREFIX
from djpcms.plugins.application import appsite

admin.autodiscover()
appsite.load()

# Admin Site
try:
    admin_url_prefix = settings.ADMIN_URL_PREFIX
    site_urls  = url(r'^%s(.*)' % admin_url_prefix[1:],    admin.site.root),
except:
    site_urls  = ()

# Applications urls
if appsite.site.count():
    site_urls += appsite.site.urls
    

# MEDIA FILES ONLY IF REQUESTED
if SERVE_STATIC_FILES:
    site_urls += (
         r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip("/"),
          'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
        ),

# if inline editing add url
if CONTENT_INLINE_EDITING.get('available',False):
    from djpcms.views import content
    baseurl = CONTENT_INLINE_EDITING.get('pagecontent', '/content/')
    site_urls += (r'^%s' % baseurl[1:], include(content.site.urls)),
    

# The djcms pagination goes as last
site_urls      += ((r'([\w/-]*)', 'djpcms.views.site.handler'),)


