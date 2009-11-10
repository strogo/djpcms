from django.conf.urls.defaults import patterns
from django.conf import settings

from djpcms.views.docview import DocView

from djpcms.urls import site_urls


# Create the documentation view handler
class DjpcmsDoc(DocView):
    name = 'djpcms'
    baseurl = '/docs/'
    DOCS_PICKLE_ROOT = '../docs/'
    
    def get_path_args(self, lang, version):
        return ("_build", "json")
djpcms_view = DjpcmsDoc()

# Add user account support



site_urls = djpcms_view.urls + site_urls
 
urlpatterns = patterns('', *site_urls)



