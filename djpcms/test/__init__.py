from .test import TestCase, TestCaseWithUser, PluginTest
from .runner import build_suite, TestLoader, TestSuiteRunner


TEST_TYPES = {'regression': TestSuiteRunner,
              'bench': None,
              'profile': None}

