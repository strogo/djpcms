import os

from djpcms.views import appsite, appview

from regression.autocomplete.models import Strategy


class ApplicationWithAutocomplete(appsite.ModelApplication):
    # RULE 2 the search_fields list
    search_fields = ['name','description']
    # RULE 3 the autocomplete view
    autocomplete = appview.AutocompleteView(regex = 'autocompletetest',
                                            display = 'name')     

# RULE 4 register as usual
appsite.site.register('/strategies/',
                      ApplicationWithAutocomplete,
                      model = Strategy)


