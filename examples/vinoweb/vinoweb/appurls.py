from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.views import appsite, appview
from djpcms.views.apps.user import UserApplication


appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)