from djpcms.views import appsite
from djpcms.apps.included import vanilla

from regression.appvanilla.models import Strategy

appurls = vanilla.Application('/strategies/',Strategy),


