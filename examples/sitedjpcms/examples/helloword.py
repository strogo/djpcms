'''Just an Hello world
'''
import djpcms

site = djpcms.MakeSite(__file__)

class TinySite(appsite.Application):
    home = appview.View(renderer = lambda djp : 'Hello World')
    
    
appurls = TinySite('/'),

    