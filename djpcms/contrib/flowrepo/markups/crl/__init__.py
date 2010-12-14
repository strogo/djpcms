import creole

from djpcms.contrib.flowrepo.markups import application


class Application(application.Application):
    code = 'crl'
    name = 'creole'
    
    def __call__(self, text):
        '''
        Parse creole text to form HTML
        '''
        document = creole.Parser(text).parse()
        return creole.HtmlEmitter(document).emit().encode('utf-8', 'ignore')
    
    
app = Application()