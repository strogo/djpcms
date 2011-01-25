from djpcms.core.api import get_root, create_page


class CreateRootPageAndUser(object):
    
    def process_request(self, request):
        site = request.site
        User = site.User
        root = get_root(request)
        if not root:
            root = create_page()
        if User:
            users = User.all()
            if not users:
                site = request.site
                url = site.get_url(User.model,'add')
                if url and url != request.path:
                    return site.http.HttpResponseRedirect(url)