import logging
import os
import sys

from djpcms import sites, MakeSite
from djpcms.test import TEST_TYPES
import djpcms.contrib as contrib
from djpcms.utils.importer import import_module

logger = logging.getLogger()

LIBRARY = 'djpcms'
CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
if CUR_DIR not in sys.path:
    sys.path.insert(0,CUR_DIR)
CONTRIB_DIR = os.path.dirname(contrib.__file__)
ALL_TEST_PATHS = (lambda test_type : os.path.join(CUR_DIR,test_type),
                  lambda test_type : CONTRIB_DIR) 


def get_tests(test_type):
    for dirpath in ALL_TEST_PATHS:
        dirpath = dirpath(test_type)
        loc = os.path.split(dirpath)[1]
        for d in os.listdir(dirpath):
            if os.path.isdir(os.path.join(dirpath,d)):
                yield (loc,d)


def import_tests(tags, test_type, can_fail):
    model_labels = []
    INSTALLED_APPS = sites.settings.INSTALLED_APPS
    tried = 0
    for loc,app in get_tests(test_type):
        model_label = '{0}.{1}'.format(loc,app)
        if tags and app not in tags:
            logger.debug("Skipping model %s" % model_label)
            continue
        tried += 1
        logger.info("Importing model {0}".format(model_label))
        if loc == 'contrib':
            model_label = 'djpcms.'+model_label
        if model_label not in INSTALLED_APPS:
            if model_label in model_labels:
                raise ValueError('Application {0} already available in testsing'
                                 .format(model_label))
            model_labels.append(model_label)
            INSTALLED_APPS.append(model_label)
        else:
            raise ValueError('Application {0} already in INSTALLED_APPS.'
                             .format(model_label))
            
    if not tried:
        print('Could not find any tests. Aborting.')
        exit()
        
    sites.setup_environment()
    # Now lets try to import the tests module them
    for model_label in model_labels:
        tests = model_label + '.tests'
        try:
            mod = import_module(tests)
        except ImportError, e:
            if can_fail:
                logger.warn("Could not import '%s'. %s" % (tests,e))
                continue
            raise
        yield mod

        
def run(tags = None, test_type = None,
        verbosity = 1, can_fail = True,
        show_list = False):
    '''Run tests'''
    test_type = test_type or 'regression'
    if test_type not in TEST_TYPES:
        print(('Unknown test type {0}. Must be one of {1}.'.format(test_type, ', '.join(TEST_TYPES))))
        exit()
    
    TestSuiteRunner = TEST_TYPES[test_type]
    if not TestSuiteRunner:
        print(('No test suite for {0}'.format(test_type)))
        exit()
    
    # Create the testing Site    
    MakeSite(test_type,'conf')

    if show_list:
        n = 0
        for name in get_tests(test_type):
            n += 1
            print(("'{1}' (from {0})".format(*name)))
        print(('\nYou can run {0} different test labels'.format(n)))
    else:
        modules = import_tests(tags, test_type, can_fail)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)

