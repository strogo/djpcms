import os
from djpcms.utils.importer import import_module


def add(code, name, handler):
    '''
    Add new markup handler
    '''
    global _default_markup, MARKUP_HANDLERS
    if not _default_markup:
        _default_markup = code
    if not MARKUP_HANDLERS.has_key(code): 
        MARKUP_HANDLERS[code] = {'name': name,
                                 'handler': handler}

def choices():
    load()
    global MARKUP_HANDLERS
    yield ('','None')
    for k,v in MARKUP_HANDLERS.items():
        yield (k,v.get('name'))

def default():
    load()
    global _default_markup
    return _default_markup

def get(name):
    load()
    global MARKUP_HANDLERS
    return MARKUP_HANDLERS.get(name,None)


def load():
    '''Load markup applications'''
    global _loaded
    if not _loaded:
        path = os.path.split(os.path.abspath(__file__))[0]
        for d in os.listdir(path):
            if os.path.isdir(os.path.join(path,d)):
                try:
                    appmod = import_module('djpcms.contrib.flowrepo.markups.{0}'.format(d))
                    app = appmod.app
                except ImportError, e:
                    pass
                else:
                    app.setup()
                    add(d,app.name,app)
        _loaded = True
        
        
_loaded = False
_default_markup = None
MARKUP_HANDLERS = {}


def help(code = 'crl'):
    c = get(code)
    if not c:
        return ''
    else:
        d = os.path.split(os.path.abspath(__file__))[0]
        templ = os.path.join(d,'code','%s-help.txt' % c['name'])
        try:
            f = open(templ,'r')
        except:
            return ''
        data = f.read()
        return c['handler'](data)

