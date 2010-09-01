#!/usr/bin/env python
#
# This file is here to run the test cases. Nothing else
#
# Type
# python testing.py test djpcms
#
import djpcms
djpcms.run_tests()

#from django.core.management import execute_manager
#try:
#    import djpcms.testsettings
#except ImportError:
#    import sys
#    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
#    sys.exit(1)
#
#if __name__ == "__main__":
#    execute_manager(djpcms.testsettings)
