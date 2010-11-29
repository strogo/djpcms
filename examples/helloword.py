from djpcms.views.decorator import getview

djpcms.MakeSite(__file__)

def simpleapp(djp):
    return 'Hello World'

class TinySite(appsite.ApplicationBase):
    home = appview.Application(renderer = simpleapp)
    
