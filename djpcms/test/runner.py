import unittest
import signal

from django.db.models import get_app, get_apps

from djpcms.utils.importer import import_module

from .environment import TestEnvironment


TestSuite = unittest.TestSuite


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
        

class DjpcmsTestRunner(unittest.TextTestRunner):
    '''Test runner adapted from django'''
    def __init__(self, verbosity=0, failfast=False, **kwargs):
        super(DjpcmsTestRunner, self).__init__(verbosity=verbosity, **kwargs)
        self.failfast = failfast
        self._keyboard_interrupt_intercepted = False

    def run(self, *args, **kwargs):
        """
        Runs the test suite after registering a custom signal handler
        that triggers a graceful exit when Ctrl-C is pressed.
        """
        self._default_keyboard_interrupt_handler = signal.signal(signal.SIGINT,
            self._keyboard_interrupt_handler)
        try:
            result = super(DjpcmsTestRunner, self).run(*args, **kwargs)
        finally:
            signal.signal(signal.SIGINT, self._default_keyboard_interrupt_handler)
        return result

    def _keyboard_interrupt_handler(self, signal_number, stack_frame):
        """
        Handles Ctrl-C by setting a flag that will stop the test run when
        the currently running test completes.
        """
        self._keyboard_interrupt_intercepted = True
        sys.stderr.write(" <Test run halted by Ctrl-C> ")
        # Set the interrupt handler back to the default handler, so that
        # another Ctrl-C press will trigger immediate exit.
        signal.signal(signal.SIGINT, self._default_keyboard_interrupt_handler)

    def _makeResult(self):
        result = super(DjpcmsTestRunner, self)._makeResult()
        failfast = self.failfast

        def stoptest_override(func):
            def stoptest(test):
                # If we were set to failfast and the unit test failed,
                # or if the user has typed Ctrl-C, report and quit
                if (failfast and not result.wasSuccessful()) or \
                    self._keyboard_interrupt_intercepted:
                    result.stop()
                func(test)
            return stoptest

        setattr(result, 'stopTest', stoptest_override(result.stopTest))
        return result


class DjpcmsTestSuiteRunner(object):
    
    def __init__(self, verbosity=1, interactive=True, failfast=True, **kwargs):
        self.verbosity = verbosity
        self.interactive = interactive
        self.failfast = failfast

    def setup_test_environment(self, **kwargs):
        self.environment = TestEnvironment(self)
        return self.environment

    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = unittest.TestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return suite

    def run_suite(self, suite, **kwargs):
        return DjpcmsTestRunner(verbosity=self.verbosity, failfast=self.failfast).run(suite)

    def teardown_databases(self, old_config, **kwargs):
        from django.db import connections
        old_names, mirrors = old_config
        # Point all the mirrors back to the originals
        for alias, connection in mirrors:
            connections._connections[alias] = connection
        # Destroy all the non-mirror databases
        for connection, old_name in old_names:
            connection.creation.destroy_test_db(old_name, self.verbosity)

    def suite_result(self, suite, result, **kwargs):
        return len(result.failures) + len(result.errors)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
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
        env = self.setup_test_environment()
        suite = self.build_suite(test_labels, extra_tests)
        env.setupdb()
        result = self.run_suite(suite)
        env.teardown()
        return self.suite_result(suite, result)
    