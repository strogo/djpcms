#:coding=utf8:
import logging

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
        self.LOGGING = getattr(settings, 'LOGGING', None)
        settings.LOGGING = self.config()
        djpcms.init_logging(clear_all = True)
    
    def config(self):
        return {}
    
    def tearDown(self):
        djpcms.init_logging(clear_all = True)        
        if self.LOGGING:
            settings.LOGGING = self.LOGGING
    
    
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



class DictHandlerTestCase(object):

    def setUp(self):
        from jogging.handlers import MockHandler
        import logging
        
        self.LOGGING = getattr(settings, 'LOGGING', None)

        settings.LOGGING = {
            'dict_handler_test': {
                'handlers': [
                    { 'handler': MockHandler(), 'level': logging.ERROR },
                    { 'handler': MockHandler(), 'level': logging.INFO },
                ],
            },
        }
        
        jogging_init()
    
    def tearDown(self):
        import logging

        # clear out all handlers on loggers
        loggers = [logging.getLogger(""), logging.getLogger("database_test"), logging.getLogger("multi_test")]
        for logger in loggers:
            logger.handlers = []
        
        # delete all log entries in the database
        for l in Log.objects.all():
            l.delete()
        
        if self.LOGGING:
            settings.LOGGING = self.LOGGING
        jogging_init()
    
    def test_basic(self):
        logger = logging.getLogger("dict_handler_test")
        error_handler = settings.LOGGING["dict_handler_test"]["handlers"][0]["handler"]
        info_handler = settings.LOGGING["dict_handler_test"]["handlers"][1]["handler"]


        logger.info("My Logging Test")
        # Make sure we didn't log to the error handler
        self.assertEquals(len(error_handler.msgs), 0)

        log_obj = info_handler.msgs[0]
        self.assertEquals(log_obj.levelname, "INFO")
        self.assertEquals(log_obj.name, "dict_handler_test")
        self.assertEquals(log_obj.msg, "My Logging Test")

class GlobalExceptionTestCase(object):
    urls = 'jogging.tests.urls'
    
    def setUp(self):
        from jogging.handlers import DatabaseHandler, MockHandler
        import logging
        
        self.LOGGING = getattr(settings, 'LOGGING', None)
        self.GLOBAL_LOG_HANDLERS = getattr(settings, 'GLOBAL_LOG_HANDLERS', None)
        self.GLOBAL_LOG_LEVEL = getattr(settings, 'GLOBAL_LOG_LEVEL', None)
        
        loggers = [logging.getLogger("")]
        for logger in loggers:
            logger.handlers = []
        
        settings.LOGGING = {}
        settings.GLOBAL_LOG_HANDLERS = [MockHandler()]
        settings.GLOBAL_LOG_LEVEL = logging.DEBUG
        
        jogging_init()
    
    def tearDown(self):
        import logging

        # clear out all handlers on loggers
        loggers = [logging.getLogger("")]
        for logger in loggers:
            logger.handlers = []
        
        # delete all log entries in the database
        for l in Log.objects.all():
            l.delete()
        
        if self.LOGGING:
            settings.LOGGING = self.LOGGING
        if self.GLOBAL_LOG_HANDLERS:
            settings.GLOBAL_LOG_HANDLERS = self.GLOBAL_LOG_HANDLERS
        if self.GLOBAL_LOG_LEVEL:
            settings.GLOBAL_LOG_LEVEL = self.GLOBAL_LOG_LEVEL
        jogging_init()
 
    def test_exception(self):
        from views import TestException
        try:
            resp = self.client.get("/exception_view")
            self.fail("Expected Exception")
        except TestException:
            pass
        root_handler = logging.getLogger("").handlers[0]

        log_obj = root_handler.msgs[0]
        self.assertEquals(log_obj.levelname, "ERROR")
        self.assertEquals(log_obj.name, "root")
        self.assertTrue("Traceback" in log_obj.msg)
