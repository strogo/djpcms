from djpcms.views.decorator import getview


def simpleapp(djp):
    return 'Hello World'

class TinySite(appsite.ApplicationBase):
    home = appview.Application(renderer = simpleapp)
    
    
if __name__ == '__main__':
    app = DjpCMS(__name__)
