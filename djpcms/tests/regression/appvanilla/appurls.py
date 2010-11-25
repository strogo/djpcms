from djpcms.views import appsite
from djpcms.views.apps import vanilla

from regression.appvanilla.models import Strategy

appsite.site.register('/strategies/',
                      vanilla.Application,
                      model = Strategy)


