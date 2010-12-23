from djpcms.views import appsite
from djpcms.views.apps import vanilla

from regression.appvanilla.models import Strategy

appurls = vanilla.Application('/strategies/',Strategy),


