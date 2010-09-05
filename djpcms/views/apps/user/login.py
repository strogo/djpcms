from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django import http

from djpcms.views import appview
from djpcms.utils.html import form, formlet, submit
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jredirect

from forms import LoginForm


__all__ = ['LogoutView','LoginView']


class LogoutView(appview.AppView):
    '''
    Logs out a user, if there is an authenticated user :)
    '''
    _methods = ('get',)
    
    def __init__(self, regex = 'logout', parent = None):
        super(LogoutView,self).__init__(regex = regex, parent = parent, isapp = False, insitemap = False)
        
    def preget(self, djp):
        request = djp.request
        params  = dict(request.GET.items())
        url     = params.get('next',None) or '/'
        user    = request.user
        if user.is_authenticated():
            logout(request)
        return http.HttpResponseRedirect(url)



class LoginView(appview.AppView):
    '''
    A Battery included Login view.
    This object can be used to login users
    '''
    def __init__(self, regex = 'login', parent = None, insitemap = False, **kwargs):
        super(LoginView,self).__init__(regex = regex, parent = parent,
                                      insitemap = insitemap, **kwargs)
        
    def title(self, page, **kwargs):
        if page:
            return 'Sign in to %s' % page.site.name
        else:
            return 'Sign in'
    
    def preget(self, djp):
        '''
        Check if user is already logged-in.
        Normally this should not append.
        '''
        if djp.request.user.is_authenticated():
            return http.HttpResponseRedirect('/')
        
    def render(self, djp, **kwargs):
        if djp.request.user.is_authenticated():
            return ''
        else:
            f = self.get_form(djp)
            return f.render()
    
    def _get_form(self, request, instance):
        return LoginForm
    
    def get_form(self, djp):
        form = self.appmodel.get_form(djp, form = self._get_form, addinputs = False)
        form.inputs.append(submit(name = 'login_user', value = 'Sign in'))
        form.inputs.append(submit(name = 'cancel', value = 'Cancel'))
        return form
        
    def get_form_url(self, request):
        url = self.page.get_absolute_url()
        if r.method == 'GET':
            next = request.GET.get("next", None)
            if next != None:
                url = '%s?next=%s' % (url,next)
        return url
    
    def default_post(self, djp):
        '''
        Try to log in
        '''
        request = djp.request
        is_ajax = request.is_ajax()
        f = self.get_form(djp)
        if f.is_valid():
            error = self.process_login_data(djp.request,f.cleaned_data)
            if not error:
                return djp.redirect(f.cleaned_data.get('next','/'))
            else:
                f.add_message(error,error=True)
        return f.json_errors(False)
        
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
