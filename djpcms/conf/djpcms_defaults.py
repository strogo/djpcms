
ADMIN_URL_PREFIX                = '/admin/'
TEMPLATE_ENGINE                 = 'django'
LANGUAGE_REDIRECT               = False
DEFAULT_TEMPLATE_NAME           = ['base.html','djpcms/base.html']
DEFAULT_VIEW_MODULE             = 'djpcms.views.pageview.pageview'
HTML_CLASSES                    = None
MAX_SEARCH_DISPLAY              = 20
CACHE_VIEW_OBJECTS              = True
DJPCMS_IMAGE_UPLOAD_FUNCTION    = None
SERVE_STATIC_FILES              = False

# Root page for user account urls
USER_ACCOUNT_HOME_URL           = '/accounts/'
JS_START_END_PAGE               = 101
EXTRA_CONTENT_PLUGIN            = None

# Analytics
GOOGLE_ANALYTICS_ID             = None
LLOOGG_ANALYTICS_ID             = None

ENABLE_BREADCRUMBS              = 1

APPLICATION_URL_MODULE          = None
APPLICATION_URL_PREFIX          = '/apps/'

DJPCMS_PLUGINS                  = ['djpcms.plugins.*']
DJPCMS_WRAPPERS                 = ['djpcms.plugins.extrawrappers']
DJPCMS_CONTENT_FUNCTION         = None
DJPCMS_MARKUP_MODULE            = 'djpcms.utils.markups'

#
# API url prefix
API_PREFIX               = 'api'

#---------------------------------- Styling
# Default grid
GRID960_DEFAULT_COLUMNS  = 12
GRID960_DEFAULT_FIXED    = True

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
CONTENT_INLINE_EDITING = {'available':True,
                          'preurl': 'edit-content',
                          'permission': None,
                          'pagecontent': '/site-content/',
                          'width': 600,
                          'height': 400}
