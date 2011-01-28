from djpcms.views import appsite, appview
from djpcms.apps.included.user import UserApplication

from stdnet.contrib.sessions.models import User

# Stdnet user aplication
appurls = UserApplication('/accounts/', User),