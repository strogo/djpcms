import logging
import os
import sys

import djpcms

# Must be here
site = djpcms.MakeSite('regression','conf')

from djpcms.test import TEST_TYPES
import djpcms.contrib as contrib

logger = logging.getLogger()

CUR_DIR     = os.path.split(os.path.abspath(__file__))[0]
if CUR_DIR not in sys.path:
    sys.path.insert(0,CUR_DIR)
CONTRIB_DIR = os.path.dirname(contrib.__file__)
TESTS_DIR   = os.path.join(CUR_DIR,'regression')
ALL_TEST_PATHS = (TESTS_DIR,CONTRIB_DIR)


def get_tests():
    tests = []
    join  = os.path.join
    for dirpath in ALL_TEST_PATHS:
        loc = os.path.split(dirpath)[1]
        for d in os.listdir(dirpath):
            if os.path.isdir(join(dirpath,d)):
                yield (loc,d)


def import_tests(tags, test_type):
    from django.db.models.loading import get_apps, load_app
    apps = settings.INSTALLED_APPS
    apptests = []
    for loc,app in get_tests():
        model_label = '{0}.{1}'.format(loc,app)
        if tags and app not in tags:
            logger.debug("Skipping model %s" % model_label)
            continue
        logger.info("Importing model %s" % model_label)
        can_fail = True
        if loc == 'contrib':
            model_label = 'djpcms.'+model_label
            can_fail = True
        try:
            mod = load_app(model_label)
        except ImportError, e:
            if can_fail:
                logger.warn("Could not import %s. %s" % (model_label,e))
                continue
            raise
        if mod:
            if model_label not in apps:
                if app in apptests:
                    raise ValueError('Application {0} already available in testsing'.format(model_name))
                apptests.append(app)
                apps.append(model_label)
    return apptests

        
def run(tags = None, test_type = None,
        verbosity = 1, can_fail = True,
        show_list = False):
    test_type = test_type or 'regression'
    if test_type not in TEST_TYPES:
        print(('Unknown test type {0}. Must be one of {1}.'.format(test_type, ', '.join(TEST_TYPES))))
        exit()
    
    TestSuiteRunner = TEST_TYPES[test_type]
    if not TestSuiteRunner:
        print(('No test suite for {0}'.format(test_type)))
        exit()
    
    if show_list:
        n = 0
        for name in get_tests(test_type):
            n += 1
            print(('{0}'.format(name)))
        print(('\nYou can run {0} different test labels'.format(n)))
    else:
        modules = import_tests(tags, test_type, can_fail)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)

