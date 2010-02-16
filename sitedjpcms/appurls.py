from django.contrib.auth.models import User

from djpcms.views.user import UserApplication
from djpcms.views import appsite

from djpcms.views.docview import DocView

#_________________________________________________ Create the documentation view handler
class DjpcmsDoc(DocView):
    name = 'djpcms-documentation'
    #baseurl = '/docs/'
    DOCS_PICKLE_ROOT = '../docs/'
    
    def get_path_args(self, lang, version):
        return ("_build", "json")


#__________________________________________________ Add user account support
appsite.site.register(User,UserApplication)
appsite.site.register(None,DjpcmsDoc)