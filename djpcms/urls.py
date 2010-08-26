import os
from django.conf.urls.defaults import *

import djpcms
from djpcms.conf import settings
from djpcms.views import appsite
from djpcms.sitemap import get_site_maps
from djpcms.utils.importlib import import_module, import_modules

if not settings.DEBUG:
    handler404 = 'djpcms.views.specials.http404view'
    handler500 = 'djpcms.views.specials.http500view'
    
import_modules(settings.DJPCMS_PLUGINS)
import_modules(settings.DJPCMS_WRAPPERS)

site_urls = ()

#ADMIN SITE
if 'djpcms.contrib.admin' in settings.INSTALLED_APPS:
    from djpcms.contrib import admin
    settings.ADMIN_MEDIA_PREFIX = '%sadmin/' % settings.MEDIA_URL
elif 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
else:
    admin = None

if admin:
    admin.autodiscover()
    try:
        admin_url_prefix = settings.ADMIN_URL_PREFIX
        #site_urls  = url(r'^{0}(.*)'.format(admin_url_prefix[1:]),    admin.site.root),
        site_urls  = url(r'^%s(.*)' % admin_url_prefix[1:],    admin.site.root),
    except:
        site_urls  = ()

appsite.load()


# MEDIA FILES ONLY IF REQUESTED
if settings.SERVE_STATIC_FILES and settings.MEDIA_URL:
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
    
    mediaroot = settings.MEDIA_ROOT
    mediasite = os.path.join(mediaroot,'site')
    site_urls += (
                  r'^%s(?P<path>.*)$' % murl, #r'^{0}site/(?P<path>.*)$'.format(murl),
                  'django.views.static.serve',
                  {'document_root': mediaroot, 'show_indexes': True}
                 ),(
                  r'^favicon.ico$',
                  'django.views.static.serve',
                  {'document_root': mediasite, 'show_indexes': True}
                 )

# Sitemap
site_urls      += (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': get_site_maps()}),


if settings.CONTENT_INLINE_EDITING['available']:
    edit = settings.CONTENT_INLINE_EDITING['preurl']
    #site_urls += ((r'{0}/([\w/-]*)'.format(edit), 'djpcms.views.handlers.editHandler'),)
    site_urls += ((r'%s/([\w/-]*)' % edit, 'djpcms.views.handlers.editHandler'),)



    
# Last the djpcms Handler
site_urls      += ((r'(.*)', 'djpcms.views.handlers.Handler'),)


