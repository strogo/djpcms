'''Module used to complement python 2.6 with skip test functionalities
which is avialable from python 2.7
'''
import time
import unittest
from functools import wraps


__all__ = ['SkipTest',
           'TestCaseBase',
           'TextTestResult',
           'TextTestRunner',
           'TestSuiteBase',
           'skip',
           'skipIf',
           'skipUnless']


class SkipTest(Exception):
    """
    Raise this exception in a test to skip it.

    Usually you can use TestResult.skip() or one of the skipping decorators
    instead of raising this directly.
    """

def _id(obj):
    return obj


def skip(reason):
    """
    Unconditionally skip a test.
    """
    def decorator(test_item):
        if not (isinstance(test_item, type) and issubclass(test_item, unittest.TestCase)):
            @wraps(test_item)
            def skip_wrapper(*args, **kwargs):
                raise SkipTest(reason)
            test_item = skip_wrapper

        test_item.__unittest_skip__ = True
        test_item.__unittest_skip_why__ = reason
        return test_item
    return decorator


def skipIf(condition, reason):
    """
    Skip a test if the condition is true.
    """
    if condition:
        return skip(reason)
    return _id


def skipUnless(condition, reason):
    """
    Skip a test unless the condition is true.
    """
    if not condition:
        return skip(reason)
    return _id


class ResultSkipMixin(object):
    """Add SkipTest functionalities
    """
    def __init__(self):
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        
    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        self.skipped.append((test, reason))
        

class TestResult(unittest.TestResult,ResultSkipMixin):
    
    def __init__(self):
        unittest.TestResult.__init__(self)
        ResultSkipMixin.__init__(self)
        
        
class TextTestResult(unittest._TextTestResult,ResultSkipMixin):
    
    def __init__(self,*args,**kwargs):
        unittest._TextTestResult.__init__(self,*args,**kwargs)
        ResultSkipMixin.__init__(self)
    

class TestCaseBase(unittest.TestCase):
    
    def defaultTestResult(self):
        return TestResult()
    
    def run(self, result=None):
        if result is None:
            result = self.defaultTestResult()
        result.startTest(self)
        
        if getattr(self.__class__, "__unittest_skip__", False):
            # If the whole class was skipped.
            try:
                result.addSkip(self, self.__class__.__unittest_skip_why__)
            finally:
                result.stopTest(self)
            return
        
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                testMethod()
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                raise
            except SkipTest as e:
                result.addSkip(self, str(e))
            except:
                result.addError(self, self._exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)


class TextTestRunner(unittest.TextTestRunner):
    
    def _makeResult(self):
        return TextTestResult(self.stream, self.descriptions, self.verbosity)
    
    def run(self, test):
        "From Python 3.1"
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()
        results = map(len, (result.expectedFailures,
                            result.unexpectedSuccesses,
                            result.skipped))
        expectedFails, unexpectedSuccesses, skipped = results
        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = len(result.failures), len(result.errors)
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result
    
    
class TestSuiteBase(unittest.TestSuite):
    pass