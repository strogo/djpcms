from django.http import *
from django.core.handlers import wsgi
from django.contrib.auth import authenticate, login, logout

Request = wsgi.WSGIRequest

HTTPException = Http404
STATUS_CODE_TEXT = wsgi.STATUS_CODE_TEXT


def is_authenticated(request):
    return request.user.is_authenticated()


def delete_test_cookie(request):
    request.delete_test_cookie()
