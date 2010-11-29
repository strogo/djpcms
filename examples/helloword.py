from djpcms.views.decorator import getview

settings = djpcms.MakeSite(__file__)

def simpleapp(djp):
    return 'Hello World'

class TinySite(appsite.ApplicationBase):
    home = appview.Application(renderer = simpleapp)
    
    
if __name__ == '__main__':
    from unuk.contrib.txweb
    app = DjpCMS(__name__)
