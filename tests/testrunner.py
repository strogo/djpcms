import logging
import os
import sys

import djpcms
import djpcms.contrib as contrib

logger = logging.getLogger()

CUR_DIR     = os.path.split(os.path.abspath(__file__))[0]
if CUR_DIR not in sys.path:
    sys.path.insert(0,CUR_DIR)
CONTRIB_DIR = os.path.dirname(contrib.__file__)
TESTS_DIR   = os.path.join(CUR_DIR,'regression')

LOGGING_MAP = {1: 'CRITICAL',
               2: 'INFO',
               3: 'DEBUG'}

ALL_TEST_PATHS = (TESTS_DIR,CONTRIB_DIR)


def get_tests():
    tests = []
    join  = os.path.join
    for dirpath in ALL_TEST_PATHS:
        loc = os.path.split(dirpath)[1]
        for d in os.listdir(dirpath):
            if os.path.isdir(join(dirpath,d)):
                tests.append((loc,d))
    return tests


def import_tests(tags,apps):
    from django.db.models.loading import get_apps, load_app
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


def setup_logging(verbosity):
    from djpcms.conf import settings
    LOGGING = settings.LOGGING
    LOGGING['loggers'] = {}
    root = {}
    LOGGING['root'] = root
    level = LOGGING_MAP.get(verbosity,None)
    if level is None:
        root['handlers'] = ['silent']
    else:
        root['handlers'] = ['console']
        root['level'] = level
    djpcms.init_logging(True)

        
def run(tags = None, verbosity = 1, interactive = True, failfast = False):
    site = djpcms.MakeSite('regression','conf')
    settings = site.settings
    setup_logging(verbosity)
    apps = settings.INSTALLED_APPS
    apptests = import_tests(tags,apps)
    
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=verbosity,
                             interactive=interactive,
                             failfast=failfast)
    test_runner.run_tests(apptests)