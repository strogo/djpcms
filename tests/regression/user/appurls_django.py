from djpcms.views import appsite, appview
from djpcms.apps.included.user import UserApplication

from django.contrib.auth.models import User

# Django user aplication
appurls = UserApplication('/accounts/', User),