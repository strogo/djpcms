import os

from django.conf.urls.defaults import url, include

import djpcms
from djpcms import sites
from djpcms.utils.log import getLogger
    
settings = sites.settings

logger = getLogger('djpcms.urls')

logger.debug("Setting up urls")
    
from djpcms.apps.djangosite.sitemap import DjpUrl, get_site_maps
from djpcms.utils.importer import import_module, import_modules

if not sites.settings.DEBUG:
    handler404 = 'djpcms.views.specials.http404view'
    handler500 = 'djpcms.views.specials.http500view'
    
site_urls = DjpUrl()


#######################################################################################
#ADMIN SITE IF AVAILABLE
if 'djpcms.contrib.admin' in settings.INSTALLED_APPS:
    settings.ADMIN_MEDIA_PREFIX = '%sadmin/' % settings.MEDIA_URL
    from django.contrib import admin
elif 'django.contrib.admin' in settings.INSTALLED_APPS:
    from django.contrib import admin
else:
    admin = None
    


if admin:
    admin.autodiscover()
    try:
        admin_url_prefix = settings.ADMIN_URL_PREFIX
        #site_urls  = url(r'^{0}(.*)'.format(admin_url_prefix[1:]),    admin.site.root),
        #site_urls.append(url(r'^%s(.*)' % admin_url_prefix[1:],    admin.site.root))
        site_urls.append((r'^%s' % admin_url_prefix[1:],    include(admin.site.urls)))
    except:
        pass
        

#######################################################################################
# MEDIA FILES ONLY IF REQUESTED
if getattr(settings,'SERVE_STATIC_FILES',False) and settings.MEDIA_URL:
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
            site_urls.append(url(r'^%s%s/(?P<path>.*)$' % (murl,app),
                                 'django.views.static.serve',
                                 {'document_root': mediapath, 'show_indexes': True}
                                 ))
    
    mediaroot = settings.MEDIA_ROOT
    mediasite = os.path.join(mediaroot,'site')
    site_urls.append(url(r'^%s(?P<path>.*)$' % murl, #r'^{0}site/(?P<path>.*)$'.format(murl),
                         'django.views.static.serve',
                         {'document_root': mediaroot, 'show_indexes': True}
                         ))
    
    site_urls.append(url(r'^favicon.ico$',
                         'django.views.static.serve',
                         {'document_root': mediasite, 'show_indexes': True}))


#################################################################################
# SITEMAP
#if settings.DJPCMS_SITE_MAP:
#    site_urls.append(url(r'^sitemap.xml$',
#                         'django.contrib.sitemaps.views.sitemap',
#                         {'sitemaps': get_site_maps()}))
