from django.contrib.auth.models import User

from djpcms.views.user import UserApplication
from djpcms.plugins.application import appsite

#__________________________________________________ Add user account support
appsite.site.register(User,UserApplication)