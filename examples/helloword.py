import djpcms
from djpcms.views import appsite, appview

djpcms.MakeSite(__file__)


class TinySite(appsite.Application):
    home = appview.View(renderer = lambda djp : 'Hello World')
    
appurls = TinySite('/'),

djpcms.UnukServe(port = 9011)