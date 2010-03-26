import os, sys
from django.core.handlers.wsgi import WSGIHandler

base = os.path.dirname(__file__)
if base not in sys.path:
    sys.path.append(base)

os.environ["DJANGO_SETTINGS_MODULE"] = "{{ module_name }}.settings"

application = WSGIHandler()