'''Dynamic content management system using Javascript and Python'''

VERSION = (0, 7, 1)


def get_version():
    if len(VERSION) == 3:
        try:
            vi = int(VERSION[2])
            v  = '%s.%s.%s' % VERSION
        except:
            v = '%s.%s_%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v

# This list is updated by the views.appsite.appsite handler
siteapp_choices = [('','-----------------')]


__version__  = get_version()
__license__  = "BSD"
__author__   = "Luca Sbardella"
__contact__  = "luca.sbardella@gmail.com"
__homepage__ = "http://github.com/lsbardel/djpcms"


def run_tests(verbosity = 1, interactive = True, failfast = False):
    '''Run tests::
    
    import djpcms
    djpcms.run_tests()'''
    import os
    import sys
    parent = lambda x : os.path.split(x)[0]
    this_dir = parent(os.path.abspath(__file__))
    path_dir = parent(this_dir)
    if path_dir not in sys.path:
        sys.path.insert(0,path_dir)
        
    from djpcms import testsettings
    from django.core.management import setup_environ
    setup_environ(testsettings)
    from django.conf import settings
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity,
                             interactive=interactive,
                             failfast=failfast)
    failures = test_runner.run_tests(('djpcms',))


