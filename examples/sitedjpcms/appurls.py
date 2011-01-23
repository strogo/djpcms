import os
from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.utils.pathtool import parentdir
from djpcms.views import appsite, appview

from djpcms.contrib.social.applications import SocialUserApplication
from djpcms.views.apps.docs import DocApplication, DocView

import sitedjpcms.signals

parent = lambda x : os.path.split(x)[0]

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocApplication):
    inherit = True
    name = 'djpcms_documentation'
    DOCS_PICKLE_ROOT = os.path.join(parentdir(os.path.abspath(__file__),2),'docs')
    
    def get_path_args(self, lang, version):
        return ("build", "json")


#__________________________________________________ Add user account support
appurls = (
           SocialUserApplication(settings.USER_ACCOUNT_HOME_URL, User),
           DjpcmsDoc('/docs/')
           )
