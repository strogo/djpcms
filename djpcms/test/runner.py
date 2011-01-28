import sys
import unittest
import signal
from inspect import isclass

import djpcms
from djpcms.utils.importer import import_module

from .environment import TestEnvironment
from .test import TextTestRunner


LOGGING_MAP = {1: 'CRITICAL',
               2: 'INFO',
               3: 'DEBUG'}


def setup_logging(verbosity):
    settings = djpcms.sites.settings
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


def build_suite(app_module):
    '''Create a test suite for the provided application module.
Look into the test module if it exists otherwise do nothing.'''
    suite = TestSuite()
    app_path = app_module.__name__.split('.')[:-1]
    try:
        test_module = import_module('{0}.tests'.format('.'.join(app_path)))
    except ImportError:
        test_module = None
    if test_module:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_module))
    return suite


class TestSuite(unittest.TestSuite):
    
    def set_env(self, env):
        self._env = env
        for test in self:
            test._env = env


class TestLoader(unittest.TestLoader):
    testClass = unittest.TestCase
    suiteClass = TestSuite
    
    def loadTestsFromModules(self, modules, itags = None):
        """Return a suite of all tests cases contained in the given module"""
        itags = itags or []
        tests = []
        for module in modules:
            for name in dir(module):
                obj = getattr(module, name)
                if (isclass(obj) and issubclass(obj, self.testClass)):
                    tag = getattr(obj,'tag',None)
                    if tag and not tag in itags:
                        continue
                    tests.append(self.loadTestsFromTestCase(obj))
        return self.suiteClass(tests)
    

class TestSuiteRunner(object):
    Loader = TestLoader
    TextTestRunner = TextTestRunner
    
    def __init__(self, verbosity=1, interactive=True, failfast=True, **kwargs):
        self.verbosity = verbosity
        self.interactive = interactive
        self.failfast = failfast

    def setup_test_environment(self, **kwargs):
        self.environment = TestEnvironment(self)
        return self.environment
    
    def build_suite(self, modules):
        loader = self.Loader()
        return loader.loadTestsFromModules(modules)
    
    def run_suite(self, suite, **kwargs):
        for test in suite:
            test.set_env(self.env)
        return self.TextTestRunner(verbosity=self.verbosity).run(suite)

    def suite_result(self, suite, result, **kwargs):
        return len(result.failures) + len(result.errors)

    def run_tests(self, modules):
        """
        Run the unit tests for all the test labels in the provided list.
        Labels must be of the form:
         - app.TestClass.test_method
            Run a single specific test method
         - app.TestClass
            Run all the test methods in a given class
         - app
            Search for doctests and unittests in the named application.

        When looking for tests, the test runner will look in the models and
        tests modules for the application.

        A list of 'extra' tests may also be provided; these tests
        will be added to the test suite.

        Returns the number of tests that failed.
        """
        setup_logging(self.verbosity)
        self.env = env = self.setup_test_environment()
        suite = self.build_suite(modules)
        env.setupdb()
        result = self.run_suite(suite)
        env.teardown()
        self.shutDown()
        return self.suite_result(suite, result)
    
    def shutDown(self):
        pass
    