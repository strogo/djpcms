DEBUG = True
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'vctw)*^2z!1fzie12zzdxf45)-rc(^7qvd(vabn&1&ogwehidr'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djpcms.contrib.messages',
    #
    'djpcms',
)

# The settings changed by the application
#==========================================================
import os
basedir = os.path.split(os.path.abspath(__file__))[0]
TEMPLATE_DIRS = (os.path.join(basedir,'templates'),)
MEDIA_ROOT = os.path.join(basedir, 'media')
DATABASES = {
    'default': {
        'ENGINE': 'sqlite3',
        'NAME': os.path.join(basedir,'vino.sqlite'),
    }
}
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.contrib.messages.context_processors.messages",
    "djpcms.core.context_processors.djpcms"
)
#=========================================================
