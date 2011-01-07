#!/usr/bin/env python
import os
import sys
from optparse import OptionParser


def makeoptions():
    parser = OptionParser()
    parser.add_option("-p", "--port",
                      type = int,
                      action="store",
                      dest="port",
                      default=8060,
                      help="Port where to run server")
    parser.add_option("-w", "--wsgi",
                      action="store",
                      dest="wsgilib",
                      default='django',
                      help="wsgi and http library to use")
    parser.add_option("-n", "--noreload",
                      action="store_false",
                      dest="use_reloader",
                      default=True,
                      help="Don't use the reloader (during debugging)")
    parser.add_option("-v", "--verbosity",
                      type = int,
                      action="store",
                      dest="verbosity",
                      default=1,
                      help="Tests verbosity level, one of 0, 1, 2 or 3")
    return parser


def makeapp(name):
    # Make sure djpcms is on the path, otherwise we assume it is
    # a development environment and we added it
    pdir = lambda d,up=1: d if not up else pdir(p.split(d)[0],up-1)
    p = os.path
    try:
        import djpcms
    except ImportError:
        path = pdir(p.abspath(__file__),2)
        sys.path.insert(0,path)
        
    from djpcms.utils.importlib import import_module
    sys.path.insert(0,p.join(pdir(p.abspath(__file__),1),name))
    mod = import_module('{0}.make'.format(name))
    return getattr(mod,'sites')
        

def serve_werkzeung(app,port,reloader):
    from werkzeug.serving import run_simple
    run_simple('localhost',
               port,
               app.wsgi,
               use_reloader=reloader)
    

def serve_django(app, port, reloader):
    pass


if __name__ == '__main__':
    options, arg = makeoptions().parse_args()
    if not arg:
        print('Supply an example name. For example vinoweb')
        exit()
    wsgi = options.wsgilib
    app = makeapp(arg[0])
    app.settings.HTTP_LIBRARY = 'wsgi'
    if wsgi == 'django':
        serve_django(app, options.port)
    elif wsgi == 'werkzeung':
        serve_werkzeung(app, options.port, options.use_reloader)
    