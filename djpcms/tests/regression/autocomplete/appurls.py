import os

from djpcms.views import appsite, appview
from djpcms.utils.pathtool import parentdir
from djpcms.views.apps import archive

from djpcms.models import SiteContent
from djpcms.views.apps.docs import DocApplication

from regression.autocomplete.forms import Strategy, StrategyForm


class StrategyApplicationWithAutocomplete(appsite.ModelApplication):
    # RULE 2 the search_fields list
    search_fields = ['name','description']
    # RULE 3 the autocomplete view
    autocomplete = appview.AutocompleteView(regex = 'autocompletetest', display = 'name')     

    
appsite.site.register('/strategies/', StrategyApplicationWithAutocomplete, model = Strategy)


