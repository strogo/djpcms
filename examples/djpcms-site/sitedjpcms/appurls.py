import os
from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.utils.pathtool import parentdir
from djpcms.views import appsite
from djpcms.views.apps.user import UserApplication
from djpcms.views.apps.docs import DocApplication, DocView

#from djpcms.contrib.djp_oauth.appurl import OAuthApplication
parent = lambda x : os.path.split(x)[0]


docdir = os.path.join(parentdir(os.path.abspath(__file__),2),'docs')

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocApplication):
    inherit = True
    name = 'djpcms_documentation'
    DOCS_PICKLE_ROOT = docdir
    
    def get_path_args(self, lang, version):
        return ("build", "json")


#__________________________________________________ Add user account support
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
#appsite.site.register(settings.USER_ACCOUNT_HOME_URL, OAuthApplication, model = User)
appsite.site.register('/docs/',DjpcmsDoc)