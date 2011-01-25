from djpcms.core.api import get_root, create_page


class CreateRootPageAndUser(object):
    
    def process_request(self, request):
        site = request.site
        User = site.User
        root = get_root(request)
        if not root:
            root = create_page()
        if User:
            users = User.objects.all()
            if not users:
                site = request.site
                url = site.get_url(User,'create')
                if url:
                    return site.http.HttpRedirect(url)