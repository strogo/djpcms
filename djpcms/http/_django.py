from django.http import *
from django.core.handlers import wsgi

Request = wsgi.WSGIRequest

HTTPException = Http404
STATUS_CODE_TEXT = wsgi.STATUS_CODE_TEXT