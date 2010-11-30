#:coding=utf8:
import logging

import django
import djpcms
from djpcms.test import TestCase
from djpcms.conf import settings
from djpcms.views import appsite, appview
from djpcms.contrib.logdb.models import Log

class TestException(Exception):
    pass

def exview(djp):
    raise TestException
    
class TestExceptionApplication(appsite.Application):
    base = appview.View(renderer = exview)

appurls = TestExceptionApplication('/test/'),


class DatabaseLogTest(TestCase):
    appurls = 'djpcms.contrib.logdb.tests'
    
    def setUp(self):
        md = 'djpcms.middleware.error.LoggingMiddleware'
        self.LOGGING = getattr(settings, 'LOGGING', None)
        settings.LOGGING = self.config()
        self.MIDDLEWARE_CLASSES = settings.MIDDLEWARE_CLASSES
        if django.get_version() < '1.3':
            if md not in settings.MIDDLEWARE_CLASSES:
                settings.MIDDLEWARE_CLASSES += md,
        djpcms.init_logging(clear_all = True)
    
    def config(self):
        return {}
    
    def tearDown(self):
        djpcms.init_logging(clear_all = True)        
        if self.LOGGING:
            settings.LOGGING = self.LOGGING
        settings.MIDDLEWARE_CLASSES = self.MIDDLEWARE_CLASSES
    
    
class SimpleDatabaseTestcase(DatabaseLogTest):
    
    def config(self):
        return {
            'version': 1,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                },
            },
            'handlers': {
                'database': {
                    'level': 'DEBUG',
                    'class': 'djpcms.contrib.logdb.handlers.DatabaseHandler',
                    'formatter': 'simple'
                },
            },
            'root': {
                'handlers': ['database'],
                'level': 'DEBUG',
            }
        }
        
    def test_basic(self):
        logger = logging.getLogger()
        self.assertEqual(len(logger.handlers),1)
        logger.warn("My Logging Test")
        self.assertEqual(Log.objects.all().count(),1)
        log_obj = Log.objects.latest()
        self.assertEquals(log_obj.level, "WARNING")
        self.assertEquals(log_obj.source, "root")
        self.assertEquals(log_obj.msg, "My Logging Test")
        self.assertTrue(log_obj.host)
        
    def testViewException(self):
        self.assertRaises(TestException, self.get, '/test/')
        log_obj = Log.objects.latest()
        self.assertEqual(Log.objects.all().count(),1)
        self.assertEquals(log_obj.level, "ERROR")
        self.assertEquals(log_obj.source, "django.request")
        msg = log_obj.msg
        self.assertTrue('WSGIRequest' in msg)
        self.assertTrue('TestException' in msg)
        self.assertTrue(': /test/' in msg)
        self.assertTrue(log_obj.host)
    
    
class ComplexHandlerTestCase(DatabaseLogTest):
    
    def config(self):
        return {
            'version': 1,
            'formatters': {
                'verbose': {
                    'format': '%(asctime)s | (p=%(process)s,t=%(thread)s) | %(levelname)s | %(name)s | %(message)s'
                },
                'simple': {
                    'format': '%(asctime)s %(levelname)s %(message)s'
                },
            },
            'handlers': {
                'mock': {
                    'level': 'INFO',
                    'class': 'djpcms.utils.log.NullHandler',
                    'formatter': 'verbose'
                },
                'database': {
                    'level': 'WARN',
                    'class': 'djpcms.contrib.logdb.handlers.DatabaseHandler',
                    'formatter': 'verbose'
                }
            },
            'loggers': {
                'database_test': {
                    'handlers': ['mock','database'],
                    'level': 'WARN',
                    'propagate': False,
                },
                'django.request': {
                    'handlers': ['database'],
                    'propagate': False
                }
            },
            'root': {
                    'handlers': ['database'],
                    'level': 'DEBUG',
            }
        }
    
    def test_basic(self):
        logger = logging.getLogger("database_test")
        self.assertEqual(len(logger.handlers),2)
        logger.warn("My Logging Test")
        self.assertEqual(Log.objects.all().count(),1)
        log_obj = Log.objects.latest()
        self.assertEquals(log_obj.level, "WARNING")
        self.assertEquals(log_obj.source, "database_test")
        self.assertEquals(log_obj.msg, "My Logging Test")
        self.assertTrue(log_obj.host)
    
    def test_multi(self):
        logger = logging.getLogger("database_test")
        logger.info("My Logging Test")
        self.assertEqual(Log.objects.all().count(),0)
        logger.warn("My Logging Test")
        log_obj = Log.objects.latest()
        self.assertEquals(log_obj.level, "WARNING")
        self.assertEquals(log_obj.source, "database_test")
        self.assertEquals(log_obj.msg, "My Logging Test")
        self.assertTrue(log_obj.host)

    def testViewException(self):
        self.assertRaises(TestException, self.get, '/test/')
        log_obj = Log.objects.latest()
        self.assertEqual(Log.objects.all().count(),1)
        self.assertEquals(log_obj.level, "ERROR")
        self.assertEquals(log_obj.source, "django.request")
        msg = log_obj.msg
        self.assertTrue('WSGIRequest' in msg)
        self.assertTrue('TestException' in msg)
        self.assertTrue(': /test/' in msg)
        self.assertTrue(log_obj.host)


