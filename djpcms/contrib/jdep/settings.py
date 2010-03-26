from django.conf import settings

# u for unix, w for windows
DEFAULT_TARGET_SYSTEM = getattr(settings,'DEFAULT_TARGET_SYSTEM','u')

TARGET_PYTHON_VERSION = getattr(settings,'TARGET_PYTHON_VERSION','2.6')

# web servers
SERVER_USER     = getattr(settings,'SERVER_USER','www-data')
SERVER_GROUP    = getattr(settings,'SERVER_GROUP',SERVER_USER)

# deployment type:
# 'mod_python': apache with mod_python
# 'mod_wsgi': apache with mod_wsgi
SERVER_TYPE     = getattr(settings,'SERVER_TYPE','mod_wsgi')
SERVER_THREADS  = getattr(settings,'SERVER_THREADS',15)
APACHE_PORT     = getattr(settings,'APACHE_PORT',90)
