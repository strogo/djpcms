'''
Install standard markup handlers
'''
from djpcms.utils.markups import addmarkup
from djpcms.utils.markups import creole

def creole_text2html(text):
    '''
    Parse creole text to form HTML
    '''
    document = creole.Parser(text).parse()
    return creole.HtmlEmitter(document).emit().encode('utf-8', 'ignore')
addmarkup('crl','creole',creole_text2html)
