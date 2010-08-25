import os
from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.views.user import UserApplication
from djpcms.views import appsite

from djpcms.views.docview import DocApplication
#from djpcms.contrib.djp_oauth.appurl import OAuthApplication
parent = lambda x : os.path.split(x)[0]

docdir = os.path.join(parent(parent(parent(os.path.abspath(__file__)))),'docs')

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocApplication):
    name = 'djpcms-documentation'
    DOCS_PICKLE_ROOT = docdir
    
    def get_path_args(self, lang, version):
        return ("build", "json")


#__________________________________________________ Add user account support
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
#appsite.site.register(settings.USER_ACCOUNT_HOME_URL, OAuthApplication, model = User)
appsite.site.register('/docs/',DjpcmsDoc)