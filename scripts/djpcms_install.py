#!/usr/bin/python

import sys
log = sys.stdout.write
err = sys.stderr.write

try:
    import settings
except ImportError, e:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %s.\n%s" % (__file__,e))
    sys.exit(1)
    
from django.core.management import setup_environ
setup_environ(settings)

from djpcms.models import Page
