from djpcms.views import appsite, appview
from djpcms.apps.included.user import UserApplication, UserClass

appurls = UserApplication('/accounts/', UserClass),