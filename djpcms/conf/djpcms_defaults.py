import logging

ROOT_URLCONF                    = 'djpcms.core.defaults.urls'
APPLICATION_URL_MODULE          = None
ADMIN_URL_PREFIX                = '/admin/'
ADMIN_MEDIA_PREFIX              = '/media/'
LANGUAGE_REDIRECT               = False
HTML_CLASSES                    = None
MAX_SEARCH_DISPLAY              = 20
CACHE_VIEW_OBJECTS              = True
DJPCMS_IMAGE_UPLOAD_FUNCTION    = None
SERVE_STATIC_FILES              = False
DJPCMS_EMPTY_VALUE              = '(None)'

# Template engine settings
TEMPLATE_ENGINE                 = 'django'
DEFAULT_TEMPLATE_NAME           = ['base.html','djpcms/base.html']

#styling
DJPCMS_STYLE                    = 'smooth'
DJPCMS_STYLING_FUNCTION         = None

#Logging
GLOBAL_LOG_LEVEL                = logging.INFO
GLOBAL_LOG_FORMAT               = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
GLOBAL_LOG_HANDLERS             = [logging.StreamHandler()]

# Root page for user account urls
USER_ACCOUNT_HOME_URL           = '/accounts/'
JS_START_END_PAGE               = 101
EXTRA_CONTENT_PLUGIN            = None

# Analytics
GOOGLE_ANALYTICS_ID             = None
LLOOGG_ANALYTICS_ID             = None

SITE_NAVIGATION_LEVELS          = 2
ENABLE_BREADCRUMBS              = 1

DJPCMS_PLUGINS                  = ['djpcms.plugins.*']
DJPCMS_WRAPPERS                 = ['djpcms.plugins.extrawrappers']
DJPCMS_MARKUP_MODULE            = 'djpcms.utils.markups'
DJPCMS_SITE_MAP                 = True

DJPCMS_USER_CAN_EDIT_PAGES      = False
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

LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'djpcms.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}