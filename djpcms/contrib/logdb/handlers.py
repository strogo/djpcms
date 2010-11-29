import datetime, logging
import platform

from django.contrib.auth.models import User
from djpcms.contrib.logdb.models import Log

HOST = platform.node()

class DatabaseHandler(logging.Handler):

    def emit(self, record):
        if hasattr(record, 'source'):
            source = record.source
        else:
            source = record.name
        user = self.get_user(record)
        client = getattr(record,'client','unknown')
        msg = self.format_msg(record)
        try:
            Log.objects.create(source=source,
                               level=record.levelname,
                               msg=msg,
                               host=HOST,
                               user=user,
                               client=client)
        except:
            # squelching exceptions sucks, but 500-ing because of a logging error sucks more
            pass
        
    def get_user(self, record):
        try:
            user = record.user
            if not isinstance(user,User):
                user = User.objects.get(username = record.user)
            if isinstance(user,User):
                return user
        except:
            return None

    def format_msg(self, record):
        return record.msg


class DatabaseErrorHandler(DatabaseHandler):
    
    def format_msg(self, record):
        try:
            request = record.request

            subject = '%s (%s IP): %s' % (
                record.levelname,
                (request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS and 'internal' or 'EXTERNAL'),
                request.path
            )
            request_repr = repr(request)
        except:
            subject = 'Error: Unknown URL'
            request_repr = "Request repr() unavailable" 
            
        if record.exc_info:
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            stack_trace = 'No stack trace available'

        return "%s\n\n%s" % (stack_trace, request_repr)
    
    
