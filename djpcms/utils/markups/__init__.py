

def add(code, name, handler):
    global _default_markup, MARKUP_HANDLERS
    if not _default_markup:
        _default_markup = code
    if not MARKUP_HANDLERS.has_key(code): 
        MARKUP_HANDLERS[code] = {'name': name,
                                 'handler': handler}

def choices():
    global MARKUP_HANDLERS
    tup = []
    for k,v in MARKUP_HANDLERS.items():
        tup.append((k,v.get('name')))
    return tup

def default():
    global _default_markup
    return _default_markup

def get(name):
    global MARKUP_HANDLERS
    return MARKUP_HANDLERS.get(name,None)

_default_markup = None
MARKUP_HANDLERS = {}
