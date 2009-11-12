from django.contrib.auth import authenticate, login, logout
from django import http

from djpcms.settings import HTML_CLASSES
from djpcms.plugins.application import appsite

from djpcms.html import quickform, link
from djpcms.utils.ajax import jredirect

from forms import LoginForm
#from tools import BaseUser

__all__ = ['LogoutApp','LoginApp']


class LogoutApp(appsite.AppView):
    '''
    Logs out a user, if there is an authenticated user :)
    '''
    _methods = ('get',)
    
    def __init__(self, url = 'logout', parent = None):
        super(LogoutApp,self).__init__(url,parent,isapp = False)
        
    def preget(self, request):
        params  = dict(request.GET.items())
        url     = params.get('next','/')
        user    = request.user
        if user.is_authenticated():
            logout(request)
        return http.HttpResponseRedirect(url)



class LoginApp(appsite.AppView):
    '''
    A Battery included Login view.
    This object can be used to login users
    '''
    def __init__(self, url = 'login', parent = None, **kwargs):
        super(LoginApp,self).__init__(url, parent, **kwargs)
        
    def title(self):
        return 'Sign in to %s' % self.page.site.name
    
    def preget(self, request):
        '''
        Check if user is already logged-in.
        Normally this should not append.
        '''
        if request.user.is_authenticated():
            return http.HttpResponseRedirect('/')
    
    def inner_content(self, request):
        data = request.GET.copy()
        return self.get_form(request, initial = data)
        
    def render(self, request, prefix, wrapper):
        '''
        Render login form according to wrapper
        '''
        if request.user.is_authenticated():
            return None
        url = self.get_url(request)
        f = self.get_form(request, prefix, wrapper, url)
        return f.render()
    
    def get_form(self, request, data = None, initial = None):
        '''
        Create the login form. This function can be reimplemented by
        a derived view
        '''
        url = self.get_url(request)
        return quickform(url     = url,
                         form    = LoginForm,
                         initial = initial,
                         data    = data,
                         submitname  = 'login_user',
                         submitvalue = 'Sign in',
                         cn = HTML_CLASSES.ajax)
        
    def get_form_url(self, request):
        url = self.page.get_absolute_url()
        if r.method == 'GET':
            next = request.GET.get("next", None)
            if next != None:
                url = '%s?next=%s' % (url,next)
        return url
    
    def ajax__login_user(self, request):
        '''
        Try to log in
        '''
        f = self.get_form(request, data = request.POST)
        if f.is_valid():
            error = self.process_login_data(request,f.cleaned_data)
            if not error:
                next = f.cleaned_data.get('next','/')
                return jredirect(url = next)
            else:
                return self.errorpost(error)
        else:
            return f.jerrors
        
    def process_login_data(self, request, data):
        '''
        process login
        '''
        username = data.get('username',None)
        password = data.get('password',None)
        if username and password:
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    r = request
                    login(r, user)
                    try:
                        r.session.delete_test_cookie()
                    except:
                        pass
                else:
                    return '%s is not active' % username
            else:
                return 'username or password not recognized'
        else:
            return 'username or password not provided'
