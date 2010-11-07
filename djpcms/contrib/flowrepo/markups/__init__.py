import os

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
    global MARKUP_HANDLERS
    yield ('','None')
    for k,v in MARKUP_HANDLERS.items():
        yield (k,v.get('name'))

def default():
    global _default_markup
    return _default_markup

def get(name):
    global MARKUP_HANDLERS
    return MARKUP_HANDLERS.get(name,None)

_default_markup = None
MARKUP_HANDLERS = {}




#______________________________________________________________________    WIKI CREOLE MARKUP
import creole
def creole_text2html(text):
    '''
    Parse creole text to form HTML
    '''
    document = creole.Parser(text).parse()
    return creole.HtmlEmitter(document).emit().encode('utf-8', 'ignore')
add('crl','creole',creole_text2html)



#______________________________________________________________________ LATEX
#from latex import text2html
#add('tex','LaTeX',text2html)


#______________________________________________________________________ MARKDOWN2
try:
    import markdown2
    
    def markdown_text2html(text):
        return markdown2.markdown(text)
    add('mkd','markdown',markdown_text2html)
except:
    pass


def help(code = 'crl'):
    c = get(code)
    if not c:
        return ''
    else:
        d = os.path.split(os.path.abspath(__file__))[0]
        templ = os.path.join(d,'%s-help.txt' % c['name'])
        try:
            f = open(templ,'r')
        except:
            return ''
        data = f.read()
        return c['handler'](data)