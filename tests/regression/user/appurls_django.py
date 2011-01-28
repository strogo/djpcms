from djpcms.views import appsite, appview
from djpcms.apps.included.user import UserApplication

# Django user aplication
appurls = UserApplication('/accounts/', UserClass),