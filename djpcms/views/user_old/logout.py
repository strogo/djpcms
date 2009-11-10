from django.contrib.auth import logout

from tools import BaseUser

class view(BaseUser):
    '''
    Logs out the user
    '''    
    def view_contents(self, request, params):
        url = params.get('next','/')
        user = request.user
        if user.is_authenticated():
            logout(request)
        return self.redirect_to(url)