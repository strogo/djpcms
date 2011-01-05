from djpcms.views import appview,appsite


class VinoApp(appsite.Application):
    search = appview.View()

appurls = [VinoApp('/')]