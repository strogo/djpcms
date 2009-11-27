from django.contrib.auth import authenticate, login, logout
from django import http

from djpcms.settings import HTML_CLASSES
from djpcms.views import appview

from djpcms.utils.html import form, formlet, submit
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jredirect

from forms import LoginForm


__all__ = ['LogoutApp','LoginApp']


class LogoutApp(appview.AppView):
    '''
    Logs out a user, if there is an authenticated user :)
    '''
    _methods = ('get',)
    
    def __init__(self, regex = 'logout', parent = None):
        super(LogoutApp,self).__init__(regex = regex, parent = parent, isapp = False)
        
    def preget(self, djp):
        request = djp.request
        params  = dict(request.GET.items())
        url     = params.get('next','/')
        user    = request.user
        if user.is_authenticated():
            logout(request)
        return http.HttpResponseRedirect(url)



class LoginApp(appview.AppView):
    '''
    A Battery included Login view.
    This object can be used to login users
    '''
    def __init__(self, regex = 'login', parent = None, **kwargs):
        super(LoginApp,self).__init__(regex = regex, parent = parent, **kwargs)
        
    def title(self, djp):
        return 'Sign in to %s' % self.page.site.name
    
    def preget(self, djp):
        '''
        Check if user is already logged-in.
        Normally this should not append.
        '''
        if djp.request.user.is_authenticated():
            return http.HttpResponseRedirect('/')
        
    def render(self, djp, **kwargs):
        f = self.get_form(djp)
        return f.render()
    
    def get_form(self, djp):
        '''
        Create the login form. This function can be reimplemented by
        a derived view
        '''
        f = LoginForm(**form_kwargs(request = djp.request))
        fhtm = form(cn = self.ajax.ajax, url = djp.url)
        fhtm['form'] = formlet(form = f,
                               submit = submit(name = 'login_user', value = 'Sign in'))
        return fhtm
        
    def get_form_url(self, request):
        url = self.page.get_absolute_url()
        if r.method == 'GET':
            next = request.GET.get("next", None)
            if next != None:
                url = '%s?next=%s' % (url,next)
        return url
    
    def ajax__login_user(self, djp):
        '''
        Try to log in
        '''
        f = self.get_form(djp)
        if f.is_valid():
            error = self.process_login_data(djp.request,f.cleaned_data)
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
