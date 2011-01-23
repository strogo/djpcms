from djpcms.models import get_root
from djpcms.forms.cms import create_page


class CreateRootPage(object):
    
    def process_request(self, request):
        root = get_root(request)
        if not root:
            root = create_page()