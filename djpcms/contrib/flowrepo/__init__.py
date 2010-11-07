'''Object aggregator, writing, bookmarking file management for django. Nothing fancy, just nuts and bolts.'''
import os
import sys

VERSION = (0, 5, 'dev')
 
def get_version():
    if len(VERSION) == 3:
        v  = '%s.%s.%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v


default_header = "Flowrepo/%s (http://github.com/lsbardel/django-flowrepo)" % get_version()   


__version__ = get_version()
__license__  = "BSD"
__author__   = "Luca Sbardella"
__contact__  = "luca.sbardella@gmail.com"
__homepage__ = "http://github.com/lsbardel/django-flowrepo"


def installcontrib():
    path = os.path.join(os.path.dirname(__file__),'contrib')
    if path not in sys.path:
        sys.path.append(path)
        
        

def runtests(verbosity = 1, interactive = True, failfast = False):
    '''Run tests::
    
    import flowrepo
    flowrepo.runtests()'''
    import os
    import sys
    try:
        import flowrepo
    except ImportError:
        parent = lambda x : os.path.split(x)[0]
        this_dir = parent(os.path.abspath(__file__))
        path_dir = parent(this_dir)
        if path_dir not in sys.path:
            sys.path.insert(0,path_dir)
        
    from flowrepo import testsettings
    from django.core.management import setup_environ
    setup_environ(testsettings)
    from django.conf import settings
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity,
                             interactive=interactive,
                             failfast=failfast)
    failures = test_runner.run_tests(('flowrepo',))
