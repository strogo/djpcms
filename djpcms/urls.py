from django.conf import settings
from django.contrib import admin
from django.conf.urls.defaults import *

import djpcms
from djpcms.settings import SERVE_STATIC_FILES, DJPCMS_PLUGINS, DJPCMS_WRAPPERS, CONTENT_INLINE_EDITING
from djpcms.views import appsite
from djpcms.sitemap import get_site_maps

if not settings.DEBUG:
    handler404 = 'djpcms.views.specials.http404view'
    handler500 = 'djpcms.views.specials.http500view'

from djpcms.plugins import loadplugins, loadwrappers
    
plugin_urls = loadplugins(DJPCMS_PLUGINS)
loadwrappers(DJPCMS_WRAPPERS)
admin.autodiscover()
appsite.load()


# Admin Site
if 'django.contrib.admin' in settings.INSTALLED_APPS:
    try:
        admin_url_prefix = settings.ADMIN_URL_PREFIX
        #site_urls  = url(r'^{0}(.*)'.format(admin_url_prefix[1:]),    admin.site.root),
        site_urls  = url(r'^%s(.*)' % admin_url_prefix[1:],    admin.site.root),
    except:
        site_urls  = ()
else:
    site_urls  = ()
    

# MEDIA FILES ONLY IF REQUESTED
if SERVE_STATIC_FILES:
    import djpcms
    import os
    djpcms_media_root = os.path.join(djpcms.__path__[0],'media','djpcms')
    murl = settings.MEDIA_URL.lstrip("/")
    site_urls += (
                    r'^%sdjpcms/(?P<path>.*)$' % murl, # r'^{0}djpcms/(?P<path>.*)$'.format(murl),
                    'django.views.static.serve',
                    {'document_root': djpcms_media_root, 'show_indexes': True}
                  ),(
                     r'^%ssite/(?P<path>.*)$' % murl, #r'^{0}site/(?P<path>.*)$'.format(murl),
                     'django.views.static.serve',
                     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
                  ),(
                     r'^favicon.ico$',
                     'django.views.static.serve',
                     {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
                  )

# Sitemap
site_urls      += (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': get_site_maps()}),

# Plugins
site_urls      += plugin_urls

if CONTENT_INLINE_EDITING['available']:
    edit = CONTENT_INLINE_EDITING['preurl']
    #site_urls += ((r'{0}/([\w/-]*)'.format(edit), 'djpcms.views.handlers.editHandler'),)
    site_urls += ((r'%s/([\w/-]*)' % edit, 'djpcms.views.handlers.editHandler'),)
    
    
loadplugins(DJPCMS_PLUGINS)
loadwrappers(DJPCMS_WRAPPERS)

# Applications urls
#if appsite.site.count():
#    site_urls += appsite.site.urls
    
# Last the djpcms Handler
site_urls      += ((r'(.*)', 'djpcms.views.handlers.Handler'),)


