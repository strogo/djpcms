'''djpcms settings for testing.
'''
import os
CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
SITE_ID = 1

# Required if testing django Integration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(CUR_DIR,'testdjpcms.sqlite')
    }
}

try:
    import django
    INSTALLED_APPS  = ['django.contrib.auth',
                       'django.contrib.sessions',
                       'django.contrib.sites',
                       'django.contrib.contenttypes',
                       'tagging']
except ImportError:
    INSTALLED_APPS = []

INSTALLED_APPS.append('djpcms')

MEDIA_ROOT = os.path.join(CUR_DIR, 'media')
TEMPLATE_DIRS = os.path.join(CUR_DIR, 'templates'),

TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.i18n",
            "django.contrib.messages.context_processors.messages",
            "djpcms.core.context_processors.djpcms"
            )

SOCIAL_OAUTH_CONSUMERS = {'oauthtest':('key','secret')}

#extensions = ['djpcms.contrib.flowrepo.markups.rst.ext.pngmath']
extensions = ['sphinx.ext.pngmath']
