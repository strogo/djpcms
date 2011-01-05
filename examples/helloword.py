import djpcms

site = djpcms.MakeSite(__file__)

class TinySite(appsite.Application):
    home = appview.View(renderer = lambda djp : 'Hello World')
    
    
appurls = TinySite('/'),


if __name__ == '__main__':
    djpcms.UnukServe(port = 9011)
    