from djpcms.views import appsite, appview
from models import SearchModel


class SearchModelApp(appsite.ModelApplication):
    search = appview.SearchView()


appurls = SearchModelApp('/test/', SearchModel),