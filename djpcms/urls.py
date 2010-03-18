import os

from django.utils.importlib import import_module
from django.conf.urls.defaults import *

import djpcms
from djpcms.contrib import admin
from djpcms.conf import settings
from djpcms.views import appsite
from djpcms.sitemap import get_site_maps

if not settings.DEBUG:
    handler404 = 'djpcms.views.specials.http404view'
    handler500 = 'djpcms.views.specials.http500view'

from djpcms.plugins import loadplugins, loadwrappers
    
plugin_urls = loadplugins(settings.DJPCMS_PLUGINS)
loadwrappers(settings.DJPCMS_WRAPPERS)
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
if settings.SERVE_STATIC_FILES:
    import djpcms
    import os
    murl = settings.MEDIA_URL.lstrip("/")
    
    # Add application media directories if they exists
    for app in settings.INSTALLED_APPS:
        if app.startswith('django.'):
            continue
        try:
            module = import_module(app)
        except:
            continue
        path   = module.__path__[0]
        app    = app.split('.')[-1]
        mediapath = os.path.join(path,'media',app)
        if os.path.isdir(mediapath):
            site_urls += (
                          r'^%s%s/(?P<path>.*)$' % (murl,app),
                          'django.views.static.serve',
                          {'document_root': mediapath, 'show_indexes': True}
                          ),
    
    mediapath = os.path.join(settings.MEDIA_ROOT,'site')
    site_urls += (
                  r'^%s(?P<path>.*)$' % murl, #r'^{0}site/(?P<path>.*)$'.format(murl),
                  'django.views.static.serve',
                  {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
                 ),(
                  r'^favicon.ico$',
                  'django.views.static.serve',
                  {'document_root': mediapath, 'show_indexes': True}
                 )

# Sitemap
site_urls      += (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': get_site_maps()}),

# Plugins
site_urls      += plugin_urls

if settings.CONTENT_INLINE_EDITING['available']:
    edit = settings.CONTENT_INLINE_EDITING['preurl']
    #site_urls += ((r'{0}/([\w/-]*)'.format(edit), 'djpcms.views.handlers.editHandler'),)
    site_urls += ((r'%s/([\w/-]*)' % edit, 'djpcms.views.handlers.editHandler'),)
    
    
loadplugins(settings.DJPCMS_PLUGINS)
loadwrappers(settings.DJPCMS_WRAPPERS)


    
# Last the djpcms Handler
site_urls      += ((r'(.*)', 'djpcms.views.handlers.Handler'),)


