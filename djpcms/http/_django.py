from django.http import *
from django.core.handlers import wsgi
from django.contrib.auth import authenticate, login, logout

from djpcms import sites

Request = wsgi.WSGIRequest

HTTPException = Http404
STATUS_CODE_TEXT = wsgi.STATUS_CODE_TEXT


def make_request(environ):
    request = Request(environ)
    request.is_xhr = request.is_ajax()
    if request.method == 'GET':
        request.args = request.GET
    elif request.method == 'POST':
        request.args = request.POST
    else:
        request.args = {}
    return request
    

def is_authenticated(request):
    return request.user.is_authenticated()


def delete_test_cookie(request):
    request.delete_test_cookie()
    
    
def path_with_query(request):
    path = request.path
    if request.method == 'GET':
        qs =  request.environ['QUERY_STRING']
        if qs:
            return path + '?' + qs
    return path


def finish_response(res, environ, start_response):
    try:
        status_text = STATUS_CODE_TEXT[res.status_code]
    except KeyError:
        status_text = 'UNKNOWN STATUS CODE'
    status = '%s %s' % (res.status_code, status_text)
    response_headers = [(str(k), str(v)) for k, v in res.items()]
    for c in res.cookies.values():
        response_headers.append(('Set-Cookie', str(c.output(header=''))))
    start_response(status, response_headers)
    return res
        

def serve(port = 8060, use_reloader = False):
    from django.core.servers.basehttp import run
    run('localhost', port, sites.wsgi)
    
