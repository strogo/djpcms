import os,sys

from django.conf import settings
from djpcms.ajaxhtml import ajaxhtml

# Not available yet. For future releases
LANGUAGE_REDIRECT      = getattr(settings, 'LANGUAGE_REDIRECT', False)
DEFAULT_TEMPLATE_NAME  = getattr(settings, 'DEFAULT_TEMPLATE_NAME', ['base.html','djpcms/base.html'])
DEFAULT_VIEW_MODULE    = getattr(settings, 'DEFAULT_VIEW_MODULE', 'djpcms.views.pageview.pageview')
USE_TINYMCE            = getattr(settings, 'USE_TINYMCE', False)
HTML_CLASSES           = getattr(settings, 'HTML_CLASSES', ajaxhtml())
MAX_SEARCH_DISPLAY     = getattr(settings, 'MAX_SEARCH_DISPLAY', 20)
DEFAULT_CODE_BASKET    = getattr(settings, 'DEFAULT_CODE_BASKET', ('code','user'))
CACHE_VIEW_OBJECTS     = getattr(settings, 'CACHE_VIEW_OBJECTS', True)

DJPCMS_IMAGE_UPLOAD_FUNCTION = getattr(settings, 'DJPCMS_IMAGE_UPLOAD_FUNCTION', None)

SERVE_STATIC_FILES     = getattr(settings, 'SERVE_STATIC_FILES', False)

# Root page for user account urls
USER_ACCOUNT_HOME_URL    = getattr(settings, 'USER_ACCOUNT_HOME_URL', '/accounts/')


JS_START_END_PAGE        = getattr(settings, 'JS_START_END_PAGE', 101)

EXTRA_CONTENT_PLUGIN     = getattr(settings, 'EXTRA_CONTENT_PLUGIN', None)
GOOGLE_ANALYTICS_ID      = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)

ENABLE_BREADCRUMBS       = getattr(settings, 'ENABLE_BREADCRUMBS', 1)

APPLICATION_URL_MODULE   = getattr(settings, 'APPLICATION_URL_MODULE', None)
APPLICATION_URL_PREFIX   = getattr(settings, 'APPLICATION_URL_PREFIX', '/apps/')

DJPCMS_PLUGINS           = getattr(settings, 'DJPCMS_PLUGINS', ['djpcms.plugins.*'])
DJPCMS_WRAPPERS          = getattr(settings, 'DJPCMS_WRAPPERS', ['djpcms.plugins.extrawrappers'])
DJPCMS_CONTENT_FUNCTION  = getattr(settings, 'DJPCMS_CONTENT_FUNCTION', 'djpcms.views.content.basecontent')
DJPCMS_MARKUP_MODULE     = getattr(settings, 'DJPCMS_MARKUP_MODULE', 'djpcms.utils.markups')

DJPCMS_PLUGIN_BASE_URL   = getattr(settings, 'DJPCMS_PLUGIN_BASE_URL', '/plugin/')



#---------------------------------- Styling

# Default grid
GRID960_DEFAULT_FIXED    = getattr(settings, 'GRID960_DEFAULT_FIXED', True)
# Style css name
DJPCMS_SITE_STYLE        = getattr(settings, 'DJPCMS_SITE_STYLE', 'smoothness')

# Inline editing configuration
# By default it is switch on
#
#    available:    boolean   whether the inline editing is on or off
#    preurl:       slug      which will be used as initial part of the editing url
#                            So if a page has the url /some/path/to/page/ its editing url will
#                            be /preurl/some/path/to/page/
#    permission:   String    dotted path to a function handling editing permissions
#    pagecontent:  String    Code of page to be used as root for site content. This page must be
#                            available in the database.
CONTENT_INLINE_EDITING = getattr(settings, 'CONTENT_INLINE_EDITING',  {'available':True,
                                                                       'preurl': 'edit-content',
                                                                       'permission': None,
                                                                       'pagecontent': '/site-content/',
                                                                       'width': 600,
                                                                       'height': 400})

libpath = os.path.join(os.path.dirname(__file__),'libs')
if libpath not in sys.path:
    sys.path.append(libpath)