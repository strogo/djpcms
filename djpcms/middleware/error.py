import sys
from logging import getLogger


logger = getLogger('django.request')


class LoggingMiddleware(object):
    '''Middleware for django version < 1.3'''    
    def process_exception(self, request, exception):
        exc_info = sys.exc_info()
        logger.error('Internal Server Error: %s' % request.path,
            exc_info=exc_info,
            extra={
                'status_code': 500,
                'request':request
            }
        )
        
 