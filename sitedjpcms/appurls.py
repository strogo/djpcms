from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.views.user import UserApplication
from djpcms.views import appsite

from djpcms.views.docview import DocApplication
from djpcms.contrib.authentication.appurl import OAuthApplication

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocApplication):
    name = 'djpcms-documentation'
    #baseurl = '/docs/'
    DOCS_PICKLE_ROOT = '../docs/'
    
    def get_path_args(self, lang, version):
        return ("_build", "json")


#__________________________________________________ Add user account support
#appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, OAuthApplication, model = User)
appsite.site.register('/docs/',DjpcmsDoc)