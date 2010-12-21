import djpcms
from djpcms.views import appsite, appview


settings = {'TEMPLATE_ENGINE': 'Jinja2'}


djpcms.MakeSite(__file__, settings)


class TinySite(appsite.Application):
    home = appview.View(renderer = lambda djp : 'Hello World')
    
    
appurls = TinySite('/'),


if __name__ == '__main__':
    djpcms.UnukServe(port = 9011)
    