from djpcms.views import appsite, appview


class Application(appsite.ModelApplication):
    search = appview.SearchView()
    add    = appview.AddView()
    view   = appview.ViewView()
    edit   = appview.EditView()