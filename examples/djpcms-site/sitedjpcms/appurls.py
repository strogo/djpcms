import os
from django.contrib.auth.models import User

from djpcms.conf import settings
from djpcms.utils.pathtool import parentdir
from djpcms.views import appsite, appview
from djpcms.views.apps.user import UserApplication
from djpcms.views.apps.docs import DocApplication, DocView

from sitedjpcms import views
import sitedjpcms.signals

parent = lambda x : os.path.split(x)[0]


class SocialUserApplication(UserApplication):
    inherit = True
    twitter_login = views.TwitterLogin()
    twitter_done = views.TwitterDone()
    
    def objectbits(self, obj):
        return {'username': obj.username}
    
    def get_object(self, *args, **kwargs):
        try:
            return self.model.objects.get(username = kwargs.get('username',None))
        except:
            return None


#from flowrepo import cms
#class FlowApplication(cms.FlowItemApplication):
#    inherit = True



docdir = os.path.join(parentdir(os.path.abspath(__file__),2),'docs')

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocApplication):
    inherit = True
    name = 'djpcms_documentation'
    DOCS_PICKLE_ROOT = docdir
    
    def get_path_args(self, lang, version):
        return ("build", "json")


#__________________________________________________ Add user account support
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, SocialUserApplication, model = User)
#appsite.site.register('/flow/', FlowApplication, model = cms.FlowItem)
appsite.site.register('/docs/',DjpcmsDoc)
