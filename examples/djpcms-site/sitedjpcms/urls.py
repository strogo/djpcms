from djpcms.urls import *
from socialauth import urls

site_urls.append((r'^%s' % settings.USER_ACCOUNT_HOME_URL[1:],
                  include('socialauth.urls')))

urlpatterns = site_urls.patterns()



