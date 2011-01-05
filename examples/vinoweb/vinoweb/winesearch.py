from winedb.providers import WineProvider
from BeautifulSoup import BeautifulStoneSoup


class WineSearch(object):
    url = 'http://api.wine-searcher.com/wine-select-api.lml'
    AFFILIATE_CODE = 'l-sbardella'
    X_VERSION = 2
    
    def __init__(self, affiliate_code):
        self.code = affiliate_code
    
    def make_url(self, name = None, vintage = None, location = None, mode = 'A', currency = None, **kwargs):
        
        if not (name or vintage):
            raise ValueError('Either anem or vintage must be supplied')
        return super(WineSearch,self).make_url(Xwinename = name,
                                               Xvintage = vintage,
                                               Xlocation = location,
                                               Xkeyword_mode = mode,
                                               Xcurrencycode = currency,
                                               Xaffiliate= self.AFFILIATE_CODE,
                                               Xversion = self.X_VERSION)
        
    def process(self, result):
        xml = BeautifulStoneSoup(result)
        code = int(xml.find('return-code').contents[0])
        type = str(xml.find('list-comment').contents[0])
        ccy = str(xml.find('list-currency-code').contents[0])
        if code == 0:
            if type =='Wine Names List':
                wines = xml.findAll('name')
                for wine in wines:
                    pass
            else:
                wines = xml.findAll('wine')
                for wine in wines:
                    merchant = str(wine.find('merchant').contents[0])
                    description = str(wine.find('merchant-description').contents[0])
                    wine = str(wine.find('wine-description').contents[0])
                    vintage = int(wine.find('vintage').contents[0])
                    size = str(wine.find('bottle-size').contents[0])
                    price = float(wine.find('price').contents[0])
                    
                    

